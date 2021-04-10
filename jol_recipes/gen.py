import sys
from xml.etree import ElementTree as ET
import textwrap


class graph_renderer():

    def __init__(self, render_recipe):
        # dynamic vars
        self.svg = ET.Element('svg', attrib={'width':'100%', 'version':"1.1", 'xmlns':"http://www.w3.org/2000/svg"})
        self.current_y = 50 #some padding for top of chart
        self.element_objs = []
        self.render_recipe = render_recipe

        # create hatched section
        self.add_defs()

        #create objects for each element
        in_split = False
        print(self.render_recipe.get('step_layout'))

        for step_id in self.render_recipe['step_layout']:

            if step_id == 'SS': #means split start
                element = element_renderer(id = step_id, is_node = False)   
                element.start_split = True
                in_split = True
                element.process_data()

            elif step_id == 'SE': #means split end
                element = element_renderer(id = step_id, is_node = False)       
                in_split = False
                element.process_data()

            else:
                element = element_renderer(id = step_id)        

                if step_id == 'Start': #first node in drawing
                    element.first_node = True
                elif step_id == 'Finish': #last node in drawing
                    element.last_node = True
                
                if in_split:
                    element.in_split = True

                element.data = self.render_recipe['steps'][str(step_id)]
                element.process_data()

            self.element_objs.append(element)                

    def render(self):

        for obj in self.element_objs:
            if obj.is_node:
                obj.draw_node(self.current_y)
                self.svg.append(obj.svg)
                self.current_y += obj.height
            else:
                obj.draw_split(self.current_y)
                self.svg.append(obj.svg)
                self.current_y += obj.height
        
        self.svg.set('height',str(self.current_y + 50))

    def get_graph(self):
        return ET.tostring(self.svg, encoding='unicode', method='html')

    def add_defs(self):
            defs = ET.Element('defs')
            
            #add hatched pattern for long nodes
            pattern = ET.Element('pattern', attrib={'id':'diagonalHatch', 'patternUnits':'userSpaceOnUse', 'width':'4', 'height':'4'})
            pattern_path = ET.Element('path', attrib={'d':'M-1,1 l2,-2 M0,4 l4,-4 M3,5 l2,-2','style':'stroke:black; stroke-width:.7'})
            pattern.append(pattern_path)
            defs.append(pattern)

            #add gradient for each node
            for step in self.render_recipe['steps']:
                step_id = step
                step_completion = str(self.render_recipe['steps'][step]['completion'])

                gradient = ET.Element('linearGradient', attrib={'id':('grd_' + str(step_id)), 'x1':'0.5', 'y1':'1', 'x2':'0.5', 'y2':'0'})
                offset1 = ET.Element('stop', attrib={'offset':'0%', 'stop-opacity':'1', 'stop-color':'#474747'})
                offset2 = ET.Element('stop', attrib={'offset':step_completion + '%', 'stop-opacity':'1', 'stop-color':'#474747'})
                offset3 = ET.Element('stop', attrib={'offset':step_completion + '%', 'stop-opacity':'1', 'stop-color':'white'})
                offset4 = ET.Element('stop', attrib={'offset':'100%', 'stop-opacity':'1', 'stop-color':'white'})
                gradient.append(offset1)
                gradient.append(offset2)
                gradient.append(offset3)
                gradient.append(offset4)
                defs.append(gradient)

            self.svg.append(defs) 

class element_renderer():
    #main node variables
    main_node_spacing_y = 25
    main_node_radius = 13
    long_step_inc = 20
    main_start_y = 40
    text_offset_x = 25
    node_text_char_width = 40
    node_text_line_spacing_y = 19
    node_extra_info_text_line_spacing_y = 30

    #ingredient node variables
    ingredient_node_spacing_y = 14 #this is the gap between bottom of one node and top of next one
    ingredient_square_side = 16

    #path horizontal poisiotns
    main_path_x = 240
    ingredient_path_x = 150
    secondary_path_x = 300

    #secondary path       
    secondary_text_offset_x = 86

    #split line
    split_height = 60 #20 for each radius, + 10 at start.

    def __init__(self,id,is_node = True):
        self.id = id
        self.is_node = is_node
        self.start_split = False
        self.in_split = False
        self.main_path = True
        self.ingredients = 0
        self.lines_text = []
        self.extra_info = False
        self.data = {}
        self.height = 0
        self.first_node = False
        self.last_node = False
        self.long_node = False
        self.y_pos = 0
        self.x_pos = 0

        self.svg = ET.Element('svg', attrib={'width':'100%'})

    def process_data(self):     
        if self.is_node:
            #process factors
            if self.data['secondary']:
                self.main_path = False
                self.x_position = self.secondary_path_x
            else:
                self.x_position = self.main_path_x
                
            self.lines_text = textwrap.wrap(self.data['instruction'], self.node_text_char_width, break_long_words=False)
            if self.data.get('extra_info'):
                self.extra_info = True

            self.ingredients = len(self.data['ingredients'])

            if self.data['long_step']:
                self.long_node = True

    def draw_node(self,svg_y_pos):

        self.svg.set('y',str(svg_y_pos))

        #every node gets some spacing above        
        self.y_pos += self.main_node_spacing_y

        if self.ingredients > 0:
            ingredients_start_y_pos = self.y_pos

            #for each ingredient, add a square node with appropriate text
            for i in range(self.ingredients):
                self.svg.append(self.draw_ingredient(i))
                self.y_pos += self.ingredient_node_spacing_y #add gap after the node

            #draw the line that sits behind the ingredient nodes
            self.svg.insert(0,self.draw_ingredients_line(ingredients_start_y_pos)) #need to insert this at the start so that the line is alawys behind the nodes

        #self.y_pos += self.main_node_radius #node is drawn for centre of radius so need to offset

        self.svg.append(self.draw_node_shape())

        self.svg.insert(0,self.draw_main_line()) #need to insert this at the start so that the main line is alawys behind the nodes

        self.height = self.y_pos

    def draw_split(self,svg_y_pos):
        
        self.svg.set('y',str(svg_y_pos))

        if self.start_split:
            path = 'M{0} 0 v10 a20,20 1 0 0 20,20 H{1} a20,20 0 0 1 20,20 v10'.format(self.main_path_x,self.secondary_path_x - 20)
        else: #therefore it is the end of a split
            path = 'M{0} 0 v10 a20,20 0 0 1 -20,20 H{1} a20,20 0 0 0 -20,20 v10'.format(self.secondary_path_x,self.main_path_x + 20)
        
        line = ET.Element('path', attrib={'d':path, 'stroke':'#add8e6', 'stroke-width':'6', 'fill':'none'})
        self.svg.append(line)
        self.y_pos += self.split_height


        self.svg.append(self.draw_main_line())
        
        self.height = self.y_pos
        
    def draw_ingredient(self,i):
        ingredient = self.data['ingredients'][i]
        
        group = ET.Element('g',attrib={})
        square = ET.Element('rect', attrib={'x':str(self.ingredient_path_x - 8),'y':str(self.y_pos),'width':str(self.ingredient_square_side),'height':str(self.ingredient_square_side),'fill':'#3D4242','stroke':'#3D4242'})
        group.append(square)
        text = ET.Element('text', attrib={'x': str(self.ingredient_path_x - 16), 'y':str(self.y_pos + (self.ingredient_square_side / 2)),'text-anchor':'end','font-size':'smaller','alignment-baseline':'middle', 'class':'chart_text'})
        text.text = ingredient['name']
        group.append(text)
        text = ET.Element('text', attrib={'x': str(self.ingredient_path_x + 16), 'y':str(self.y_pos + (self.ingredient_square_side / 2)),'text-anchor':'start','font-size':'smaller','font-style':'italic','alignment-baseline':'middle'})
        text.text = str(ingredient['quantity']) + ' ' + str(ingredient['unit'])
        group.append(text)
        
        # increment y_pos for height of ingredient node
        self.y_pos += self.ingredient_square_side

        return group

    def draw_ingredients_line(self,ingredients_start_y_pos):
        top_pos = ingredients_start_y_pos + 5 #offset by 5 so line is not visible above top node
        
        self.y_pos -= 10 #offset to stop line after ingredient nodes being too long vertically
        
        if self.main_path:
            s_path = 'M{0} {1} V{2} a20,20 0 0 0 20,20 H{3} a20,20 0 0 1 20,20 v5'.format(self.ingredient_path_x,top_pos,self.y_pos,self.main_path_x-20)
            s_path = ET.Element('path', attrib={'d':s_path, 'stroke':'#D7DADA', 'stroke-width':'6', 'fill':'none'})
        else:
            s_path = 'M{0} {1} V{2} a20,20 0 0 0 20,20 H{4} m12 0 H{3} a20,20 0 0 1 20,20 v5'.format(self.ingredient_path_x,top_pos,self.y_pos,self.secondary_path_x-20,self.main_path_x-6)
            s_path = ET.Element('path', attrib={'d':s_path, 'stroke':'#add8e6', 'stroke-width':'6', 'fill':'none'})
        
        self.y_pos += 45 #this is the height of the 'S' at the bottom of the ingredient path

        return s_path

    def draw_node_shape(self):
       
        # apply offset because node is drawn from centre, not top of radius
        
        node_draw_y_pos = self.y_pos + self.main_node_radius
       
        calc_node_height = 0
        calc_text_height = 0

        group = ET.Element('g')

        if self.long_node:  
            oval_middle_length = self.data['long_step'] * self.long_step_inc

            #first oval outline  
            s_path = 'M{0},{1} v{2} a{3},{3} 1 0 0 {3},{3} a{3},{3} 1 0 0 {3},-{3} v-{2} a-{3},{3} 1 0 0 -{3},-{3} a{3},{3} 1 0 0 -{3},{3}'.format(self.x_position - 13, node_draw_y_pos, oval_middle_length, self.main_node_radius)
            oval = ET.Element('path', attrib={'d':s_path, 'fill':'white','stroke':'#929292'})
            group.append(oval)
            
            #then the fill
            s_path = 'M{0},{1} v{2} a{3},{3} 1 0 0 {3},{3} a{3},{3} 1 0 0 {3},-{3} v-{2} a-{3},{3} 1 0 0 -{3},-{3} a{3},{3} 1 0 0 -{3},{3}'.format(self.x_position - 11, node_draw_y_pos, oval_middle_length, self.main_node_radius - 2)
            oval = ET.Element('path', attrib={'d':s_path, 'fill':'url(#diagonalHatch)'})
            group.append(oval)

            calc_node_height += (2 * self.main_node_radius) + oval_middle_length

        else:
            #first cirlce is the outline
            circle = ET.Element('circle', attrib={'cx': str(self.x_position),'cy':str(node_draw_y_pos),'r': str(self.main_node_radius), 'fill':'white','stroke':'#929292'})
            group.append(circle)

            #second circle is for the fill
            circle = ET.Element('circle', attrib={'cx': str(self.x_position),'cy':str(node_draw_y_pos),'r': str(self.main_node_radius - 2), 'fill':'url(#grd_' + str(self.id) + ')'})
            group.append(circle)

            calc_node_height += (2 * self.main_node_radius)
        
        #work out how tall the text will be
        if self.lines_text:
            calc_text_height += len(self.lines_text) * self.node_text_line_spacing_y
        
        if self.extra_info == True:
            calc_text_height += self.node_extra_info_text_line_spacing_y

        group.append(self.draw_node_text(calc_text_height))

        self.y_pos += max(calc_text_height, calc_node_height)

        return group

    def draw_node_text(self,calc_text_height):
        
        g = ET.Element('g', attrib={})

        text_y_pos = self.y_pos + 2

        if self.in_split:
            text_x_pos = self.secondary_path_x + self.text_offset_x
        else:
            text_x_pos = self.main_path_x + self.text_offset_x

        fo = ET.Element('foreignObject', attrib={'x':str(text_x_pos), 'y':str(text_y_pos), 'height':str(len(self.lines_text) * self.node_text_line_spacing_y + 50), 'width':'100%'})
        fo.append(ET.Element('body', attrib={'xmlns':'http://www.w3.org/1999/xhtml'}))

        text_area = ET.Element('textarea', attrib={'rows':str(len(self.lines_text)),'cols':str(self.node_text_char_width),'disabled':'','wrap':'soft','class':'chart_textarea chart_text'})
        
        text_block = ''
        for line in self.lines_text:
            text_block += str(line)
            text_block += '\r\n'
        text_area.text = text_block
        
        p1 = ET.Element('p', attrib={'class':'chart_p'})
        p1.append(text_area)
        fo.append(p1)

        

        # draw the connecting line if required
        if self.in_split and self.main_path:
            path = 'M{0} {1} H{2}'.format(self.main_path_x,text_y_pos + 11,text_x_pos - 5)
            path = ET.Element('path', attrib={'d':path,'stroke':'#929292'})
            self.svg.insert(0,path)

        #add the 'extra info' section if required
        if self.extra_info:
            p2 = ET.Element('p', attrib={'class':'chart_p'})

            #tspan =  ET.Element('tspan', attrib={'x':str(text_x_pos),'y':str(text_y_pos + (len(self.lines_text) * 19)),'alignment-baseline':'middle'})
            a = ET.Element('a', attrib={'alignment-baseline':'middle','tabindex':"0", 'class':"chart_a chart_text", "role":"button", 'data-toggle':"popover", "data-trigger":"focus", 'data-placement':"bottom", 'data-content':self.data['extra_info']})
            a.text = "Click for More Details..."
            #tspan.append(a)
            p2.append(a)
            fo.append(p2)
        
        g.append(fo)

        return g 

    def draw_main_line(self):
        
        g = ET.Element('g', attrib={})
        
        if self.first_node:
            line_start = self.main_node_spacing_y + self.main_node_radius
        else:
            line_start = 0

        if self.in_split: #if we are in a split state we draw two main lines - one per side of the split
            path1 = 'M{0},{1} V{2}'.format(self.main_path_x, line_start, self.y_pos)
            path2 = 'M{0},{1} V{2}'.format(self.secondary_path_x, line_start, self.y_pos)    
            g.append(ET.Element('path', attrib={'d':path1, 'stroke':'#D7DADA', 'stroke-width':'6'}))
            g.append(ET.Element('path', attrib={'d':path2, 'stroke':'#add8e6', 'stroke-width':'6'}))
        else:
            path = 'M{0},{1} V{2}'.format(self.main_path_x, line_start, self.y_pos)
            g.append(ET.Element('path', attrib={'d':path, 'stroke':'#D7DADA', 'stroke-width':'6'}))
        
        return g


############## END OF CLASS ######################

def generate(render_recipe): 
    if render_recipe and render_recipe.get('step_layout'):
        
        obj_graph_renderer = graph_renderer(render_recipe = render_recipe)
        obj_graph_renderer.render()
        return obj_graph_renderer.get_graph()

    else:
        return False
