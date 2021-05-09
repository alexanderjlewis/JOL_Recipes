import sys
from xml.etree import ElementTree as ET
import textwrap


class graph_renderer():

    def __init__(self, render_recipe, quantity_required = ''):
        # dynamic vars
        self.svg = ET.Element('svg', attrib={'version':"1.1", 'xmlns':"http://www.w3.org/2000/svg"})
        self.current_y = 0
        self.element_objs = []
        self.render_recipe = render_recipe

        # create hatched section
        self.add_defs()

        #create objects for each element
        in_split = False
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
            pattern_path = ET.Element('path', attrib={'id':'diagonalHatchPattern', 'd':'M-1,1 l2,-2 M0,4 l4,-4 M3,5 l2,-2'})
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
    node_text_line_spacing_y = 15
    node_extra_info_text_line_spacing_y = 30

    #ingredient node variables
    ingredient_node_spacing_y = 14 #this is the gap between bottom of one node and top of next one
    ingredient_square_side = 16
    ingredient_name_text_char_width = 17
    ingredient_qty_text_char_width = 9
    ingredient_text_line_spacing_y = 13
    ingredient_text_x_offset = 16

    #path horizontal poisiotns
    main_path_x = 240
    ingredient_path_x = 150
    secondary_path_x = 320

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
        self.time = False
        self.data = {}
        self.height = 0
        self.first_node = False
        self.last_node = False
        self.long_node = False
        self.y_pos = 0
        self.x_pos = 0

        self.svg = ET.Element('svg')

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

            if self.data['time']:
                self.time = True

    def draw_node(self,svg_y_pos):

        self.svg.set('y',str(svg_y_pos))

        #every node gets some spacing above        
        self.y_pos += self.main_node_spacing_y

        #1) Check if ingredients are require for this node
        if self.ingredients > 0:
            ingredients_start_y_pos = self.y_pos

            #1a) for each ingredient, add a square node with appropriate text
            for i in range(self.ingredients):
                self.svg.append(self.draw_ingredient(i))
                
            #1b) draw the line that sits behind the ingredient nodes
            self.svg.insert(0,self.draw_ingredients_line(ingredients_start_y_pos)) #need to insert this at the start so that the line is alawys behind the nodes

        #2) Draw the round/oval node (this includes adding the text)
        self.svg.append(self.draw_node_shape())

        #3) Draw the main vertical line
        self.svg.insert(0,self.draw_main_line()) #need to insert this at the start so that the main line is alawys behind the nodes

        self.height = self.y_pos

    def draw_split(self,svg_y_pos):
        
        self.svg.set('y',str(svg_y_pos))

        if self.start_split:
            path = 'M{0} 0 v10 a20,20 1 0 0 20,20 H{1} a20,20 0 0 1 20,20 v10'.format(self.main_path_x,self.secondary_path_x - 20)
        else: #therefore it is the end of a split
            path = 'M{0} 0 v10 a20,20 0 0 1 -20,20 H{1} a20,20 0 0 0 -20,20 v10'.format(self.secondary_path_x,self.main_path_x + 20)
        
        line = ET.Element('path', attrib={'d':path, 'class':'secondary_line'})
        self.svg.append(line)
        self.y_pos += self.split_height


        self.svg.append(self.draw_main_line())
        
        self.height = self.y_pos
        
    def draw_ingredient(self,i):
        ingredient = self.data['ingredients'][i]

        name_text_lines = textwrap.wrap(ingredient['name'], self.ingredient_name_text_char_width, break_long_words=False)
        name_number_of_lines = len(name_text_lines)

        qty_text_string = str(ingredient['quantity']) + ' ' + str(ingredient['unit'])
        qty_text_lines = textwrap.wrap(qty_text_string, self.ingredient_qty_text_char_width, break_long_words=False)
        qty_number_of_lines = len(qty_text_lines)

        max_lines = max(name_number_of_lines,qty_number_of_lines)

        node_height = ((max_lines - 1) * self.ingredient_text_line_spacing_y) + self.ingredient_square_side

        group = ET.Element('g',attrib={})

        # add the ingredient name text
        if name_number_of_lines > 1: #more then one line
            base_y_pos = self.y_pos + (self.ingredient_square_side / 2) + (self.ingredient_text_line_spacing_y * ((max_lines - name_number_of_lines) / 2))
            for i in range(name_number_of_lines):
                text = ET.Element('text', attrib={'x': str(self.ingredient_path_x - self.ingredient_text_x_offset), 'y':str(base_y_pos + (i * self.ingredient_text_line_spacing_y)),'text-anchor':'end','alignment-baseline':'middle', 'class':'chart_text'})
                text.text = name_text_lines[i]
                group.append(text)
        else: #only one line
            text = ET.Element('text', attrib={'x': str(self.ingredient_path_x - self.ingredient_text_x_offset), 'y':str(self.y_pos + (node_height / 2)),'text-anchor':'end','alignment-baseline':'middle', 'class':'chart_text'})
            text.text = ingredient['name']
            group.append(text)

        # add the qty name text
        if qty_number_of_lines > 1: #more then one line
            base_y_pos = self.y_pos + (self.ingredient_square_side / 2) + (self.ingredient_text_line_spacing_y * ((max_lines - qty_number_of_lines) / 2))
            for i in range(qty_number_of_lines):
                text = ET.Element('text', attrib={'x': str(self.ingredient_path_x + self.ingredient_text_x_offset), 'y':str(base_y_pos + (i * self.ingredient_text_line_spacing_y)),'text-anchor':'start','alignment-baseline':'middle', 'class':'chart_text'})
                text.text = qty_text_lines[i]
                group.append(text)
        else: #only one line
            text = ET.Element('text', attrib={'x': str(self.ingredient_path_x + self.ingredient_text_x_offset), 'y':str(self.y_pos + (node_height / 2)),'text-anchor':'start','alignment-baseline':'middle', 'class':'chart_text'})
            text.text = qty_text_string
            group.append(text)
        
        #draw the square for the ingredient node
        square = ET.Element('rect', attrib={'x':str(self.ingredient_path_x - 8),'y':str(self.y_pos),'width':str(self.ingredient_square_side),'height':str(node_height),'class':'ingredient_square'})
        group.append(square)

        # increment y_pos for height of ingredient node
        self.y_pos += node_height
        
        # increment y_pos to add some space after the node
        self.y_pos += self.ingredient_node_spacing_y

        return group

    def draw_ingredients_line(self,ingredients_start_y_pos):
        top_pos = ingredients_start_y_pos + 5 #offset by 5 so line is not visible above top node
        
        self.y_pos -= 10 #offset to stop line after ingredient nodes being too long vertically
        
        if self.main_path:
            s_path = 'M{0} {1} V{2} a20,20 0 0 0 20,20 H{3} a20,20 0 0 1 20,20 v5'.format(self.ingredient_path_x,top_pos,self.y_pos,self.main_path_x-20)
            s_path = ET.Element('path', attrib={'d':s_path, 'class':'main_line'})
        else:
            s_path = 'M{0} {1} V{2} a20,20 0 0 0 20,20 H{4} m12 0 H{3} a20,20 0 0 1 20,20 v5'.format(self.ingredient_path_x,top_pos,self.y_pos,self.secondary_path_x-20,self.main_path_x-6)
            s_path = ET.Element('path', attrib={'d':s_path, 'class':'secondary_line'})
        
        self.y_pos += 45 #this is the height of the 'S' at the bottom of the ingredient path

        return s_path

    def draw_node_shape(self):
       
        # apply offset because node is drawn from centre, not top of radius
        
        node_draw_y_pos = self.y_pos + self.main_node_radius
       
        calc_node_height = 0
        calc_text_height = 0

        group = ET.Element('g')

        #1) work out how tall the node shape will be
        if self.long_node:  
            oval_middle_length = self.data['long_step'] * self.long_step_inc

            #first oval outline  
            s_path = 'M{0},{1} v{2} a{3},{3} 1 0 0 {3},{3} a{3},{3} 1 0 0 {3},-{3} v-{2} a-{3},{3} 1 0 0 -{3},-{3} a{3},{3} 1 0 0 -{3},{3}'.format(self.x_position - 13, node_draw_y_pos, oval_middle_length, self.main_node_radius)
            oval = ET.Element('path', attrib={'d':s_path, 'class':'node_outline'})
            group.append(oval)
            
            #then the fill
            s_path = 'M{0},{1} v{2} a{3},{3} 1 0 0 {3},{3} a{3},{3} 1 0 0 {3},-{3} v-{2} a-{3},{3} 1 0 0 -{3},-{3} a{3},{3} 1 0 0 -{3},{3}'.format(self.x_position - 11, node_draw_y_pos, oval_middle_length, self.main_node_radius - 2)
            oval = ET.Element('path', attrib={'d':s_path, 'fill':'url(#diagonalHatch)'})
            group.append(oval)

            calc_node_height += (2 * self.main_node_radius) + oval_middle_length

        else:
            #first cirlce is the outline
            circle = ET.Element('circle', attrib={'cx': str(self.x_position),'cy':str(node_draw_y_pos),'r': str(self.main_node_radius), 'class':'node_outline'})
            group.append(circle)

            #second circle is for the fill
            circle = ET.Element('circle', attrib={'cx': str(self.x_position),'cy':str(node_draw_y_pos),'r': str(self.main_node_radius - 2), 'fill':'url(#grd_' + str(self.id) + ')'})
            group.append(circle)

            calc_node_height += (2 * self.main_node_radius)
        
        #2) work out how tall the text will be
        if self.lines_text:
            calc_text_height += len(self.lines_text) * self.node_text_line_spacing_y
        if self.extra_info:
            calc_text_height += self.node_extra_info_text_line_spacing_y

        group.append(self.draw_node_text(calc_text_height))

        #3) take the max of 1) and 2)
        self.y_pos += max(calc_text_height, calc_node_height)

        return group

    def draw_node_text(self,calc_text_height):
        
        g = ET.Element('g', attrib={})

        text_y_pos = self.y_pos + 2

        if self.in_split:
            text_x_pos = self.secondary_path_x + self.text_offset_x
        else:
            text_x_pos = self.main_path_x + self.text_offset_x

        # add the main node text
        text_area = ET.Element('text', attrib={'x':str(text_x_pos), 'y':str(text_y_pos), 'class':'chart_text'})

        for line in self.lines_text:
            text_line = ET.Element('tspan', attrib={'x':str(text_x_pos) ,'dy':str(self.node_text_line_spacing_y)})
            text_line.text = line
            text_area.append(text_line)

        g.append(text_area)

        #add the 'extra info' section if required
        if self.extra_info:

            extra_info_text_y_pos = text_y_pos + (self.node_text_line_spacing_y * len(self.lines_text)) + self.node_text_line_spacing_y + 10

            text_area = ET.Element('text', attrib={'x':str(text_x_pos), 'y':str(extra_info_text_y_pos), 'class':'chart_text'})
            a = ET.Element('a', attrib={'alignment-baseline':'middle','tabindex':"0", 'class':"chart_a", "role":"button", 'data-toggle':"popover", "data-trigger":"focus", 'data-placement':"bottom", 'data-content':self.data['extra_info']})
            a.text = "Click for More Details..."
            text_area.append(a)

            g.append(text_area)

        # draw the connecting line if required
        if self.in_split:
            if self.main_path:
                path = 'M{0} {1} H{2}'.format(self.main_path_x,text_y_pos + 11,text_x_pos - 5)
                path = ET.Element('path', attrib={'d':path,'class':'text_connection_line'})
                self.svg.insert(0,path)
                if self.time:
                    path = 'M{0} {1} H{2}'.format(self.main_path_x,text_y_pos + 11,self.main_path_x - self.text_offset_x + 5)
                    path = ET.Element('path', attrib={'d':path,'class':'text_connection_line'})
                    self.svg.insert(0,path)
            else:
                path = 'M{0} {1} H{2}'.format(self.secondary_path_x,text_y_pos + 11,text_x_pos - 5)
                path = ET.Element('path', attrib={'d':path,'class':'text_connection_line'})
                self.svg.insert(0,path)
                if self.time:
                    path = 'M{0} {1} H{2}'.format(self.secondary_path_x,text_y_pos + 11,self.main_path_x - self.text_offset_x + 5)
                    path = ET.Element('path', attrib={'d':path,'class':'text_connection_line'})
                    self.svg.insert(0,path)
        else:
            path = 'M{0} {1} H{2}'.format(self.main_path_x,text_y_pos + 11,text_x_pos - 5)
            path = ET.Element('path', attrib={'d':path,'class':'text_connection_line'})
            self.svg.insert(0,path)
            if self.time:
                path = 'M{0} {1} H{2}'.format(self.main_path_x,text_y_pos + 11,self.main_path_x - self.text_offset_x + 5)
                path = ET.Element('path', attrib={'d':path,'class':'text_connection_line'})
                self.svg.insert(0,path)

        
        #add the 'time' text
        if self.time:
            time_text = ET.Element('text', attrib={'x':str(self.main_path_x - self.text_offset_x), 'y':str(text_y_pos + 15), 'class':'chart_text', 'text-anchor':'end'})
            time_text.text = self.data['time']
            g.append(time_text)

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
            g.append(ET.Element('path', attrib={'d':path1, 'class':' main_line'}))
            g.append(ET.Element('path', attrib={'d':path2, 'class':' secondary_line'}))
        else:
            path = 'M{0},{1} V{2}'.format(self.main_path_x, line_start, self.y_pos)
            g.append(ET.Element('path', attrib={'d':path, 'class':' main_line'}))
        
        return g


############## END OF CLASS ######################

def generate(recipe):
    
    if recipe and recipe.get('step_layout'): 
        obj_graph_renderer = graph_renderer(recipe)
        obj_graph_renderer.render()
        return obj_graph_renderer.get_graph()

    else:
        return False
