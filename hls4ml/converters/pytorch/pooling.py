import math
from hls4ml.converters.pytorch_to_hls import pytorch_handler
from hls4ml.converters.utils import * #Get parse data format and the two padding functions, which is the whole file.... 


#Using onnx branch, not master branch hls4ml version

pooling_layers = ['MaxPool1d', 'MaxPool2d', 'AvgPool1d', 'AvgPool2d']
@pytorch_handler(*pooling_layers) #Iterate through the 4 types of pooling layers

def parse_pooling_layer(pytorch_layer, layer_name, input_shapes, data_reader, config):
    
    """"
    Suppose model has attribute pool1, model.pool1 = maxpool2D(a,b,c)
    pytorch_layer = model_name.pool1, model_name.pool2, etc
    """
    layer = {}
    
    layer['name'] = layer_name # i.e. model.pool would give pool
    layer['class_name'] = pytorch_layer.__class__.__name__.replace("Pool1d", "Pool1D").replace("Pool2d", "Pool2D") # i.e. maxpool2D, maxpool1d, etc
    layer['data_format'] = 'channels_first' #By Pytorch default, cannot change
    
    ### Unsure about what this does ###
    #layer['inputs'] = input_names 
    
    #Check if 1D or 2D. 1, 2 is the second to last character
    #if int(layer['class_name'][-2]) == 1:
    if "Pool1D" in layer['class_name']:   
        '''Compute number of channels'''
        (layer['n_in'], layer['n_filt']) = parse_data_format(input_shapes[0], 'channels_first')
        
        #prepare padding input
        layer['pool_width'] = pytorch_layer.kernel_size
        layer['stride_width'] = pytorch_layer.stride
        #pytorch_layer.stride[0] from another document
        #layer['padding'] = pytorch_layer.padding
        if pytorch_layer.padding == 0: # No padding, i.e., 'VALID' padding in Keras/Tensorflow
            layer['padding'] = 'valid'
        else: #Only 'valid' and 'same' padding are available in Keras
            layer['padding'] = 'same'
        
        '''Compute padding 1d'''
        #hls4ml layers after padding
        ( layer['n_out'], layer['pad_left'], layer['pad_right'] ) = compute_padding_1d(layer['padding'], layer['n_in'],layer['stride_width'], layer['pool_width'])
        
        #Assuming only 'channels_first' is available
        output_shape=[input_shapes[0][0], layer['n_filt'], layer['n_out']]
        
    elif "Pool2D" in layer['class_name']:
        
        '''Compute number of channels'''
        (layer['in_height'], layer['in_width'], layer['n_filt']) = parse_data_format(input_shapes[0], 'channels_first')

        layer['stride_height'] = pytorch_layer.stride[0]
        layer['stride_width'] = pytorch_layer.stride[1]
        
        layer['pool_height'] = pytorch_layer.kernel_size[0]
        layer['pool_width'] = pytorch_layer.kernel_size[1]
        
        #Side note, it seems that pool width and height is the same
        layer['padding'] = pytorch_layer.padding[0] 
        #pytorch_layer.padding is an object with attributes lower()--> Should output 'same' or 'valid' or otherwise unsupported

        #hls4ml layers after padding
        (
        layer['out_height'], layer['out_width'], 
        layer['pad_top'], layer['pad_bottom'], 
        layer['pad_left'], layer['pad_right']
        ) = compute_padding_2d(
        layer['padding'],
        layer['in_height'], layer['in_width'],
        layer['stride_height'],layer['stride_width'],
        layer['pool_height'], layer['pool_width'])
        #Good
        #Only channels_first is available in pytorch. cannot change
        output_shape=[input_shapes[0][0], layer['n_filt'], layer['out_height'], layer['out_width']]
    
    
    #Return parsed layer and output shape
    return layer, output_shape         
        
        #Checking if git picks up this
        
        