import numpy as np
import time
def get_normed_3d_coord(far_point, frame_shape, gs, final_scale=1, rel_tp = None):
    # far_point is the 2d coordinate of the reference point
    # gs is the disparity (depth) map
    # rectified pair is the image frame that we are working in
    # final scale is m in the 0 -> m range that we want our 3d coordinates to
    # be normalized between
    draw_point = np.zeros(3)
    if far_point is None:
        return draw_point
    if far_point[0] < gs.shape[0] and far_point[1] < gs.shape[1]:
        #print("Disparity at finger is, ", gs[far_point])        
        # draw point is a 3d point normalized between -final_scale and final_scale
        # scale the data if the frame is not square
        x_scale = final_scale
        y_scale = final_scale
        if frame_shape[0] != frame_shape[1]:
            if frame_shape[1] < frame_shape[0]:
                y_scale = final_scale * (float(frame_shape[0])/float(frame_shape[1]))
            else:
                x_scale = final_scale * (float(frame_shape[1])/float(frame_shape[0]))
        #print("frame shape:", frame_shape, "\nx scale:", x_scale, "\ny scale:", y_scale, "\nx point:", far_point[1], "y point", far_point[0])

        # keep in mind that frame_shape[0] is the size of the y axis, but 
        # far_point[0] is the x point. Thus the two need to be interchanged
        # to scale properly.
        draw_point[0] = x_scale - (far_point[0]/frame_shape[1]*x_scale)
        draw_point[1] = y_scale - (far_point[1]/frame_shape[0]*y_scale)
        print('current DM val: ', gs[far_point])
        if rel_tp is None:
            draw_point[2] = (gs[far_point]*final_scale)
        else:
            draw_point[2] = (gs[rel_tp[0], rel_tp[1]]*final_scale)
       
        if (draw_point[2] == 0):
            print('out of depth map range')

        # normalize this depth map point relative to the top percentile of the data
        draw_point[2] = (draw_point[2]*1.0)/np.percentile(gs,98)
        if (draw_point[2] > 1):
            draw_point[2] = 1
    
    #This final step causes the values to be more sensible
    # this way, y=0 is the bottom and z=0 is the front of the data
    return draw_point


def render_drawing(model, draw_point, uart_val,count, lNode, pressed_key=0xff):
#Dust 3d code using model
    
    if(lNode == 0):
        lNode = model.genId()
        model.add_n_node(lNode, draw_point[0], draw_point[1], draw_point[2], .01)
    elif((uart_val & 0x02)== 0x02  or (pressed_key & 0xFF == ord('1'))):
        nNode = model.genId()
        model.add_a_node(nNode, lNode, draw_point[0], draw_point[1], draw_point[2], .01)
       # model.add_edge(lNode,nNode)
        lNode = nNode
        count += 1
        model.reply()
   # elif((uart_val & 0x01) == 0x01):
        export = model.exportAsObj(1)
        if(export == 1):
            print("export Complete")
        else:
            export = model.exportAsObj(1)
            print("take 2")
    elif((uart_val & 0x04) == 0x04):
        lNode = 0
    return count, lNode       
