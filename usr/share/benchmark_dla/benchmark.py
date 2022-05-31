import os
import sys
import re
import numpy as np
import logging

ARG_AUTO_RUN = 'auto'
INFERENCE_CNT = 10
RUN_ALL = 'ALL'
DIRTY = 1
CLEAR_DIRTY = 0

TIME = 'avg inference time:'
INIT_TIME = TIME + ' FAILED'

def tflite_2_dla(tflite_model, target, dla_model):
    # compile for specific target
    if os.path.exists(dla_model):
        os.remove(dla_model)
    
    batcmd = ('ncc-tflite -arch %s %s -o %s' % (target, tflite_model, dla_model) )
    result = os.popen(batcmd).read()
    logging.debug(result)
        
def find_input_output_info_from_dla(dla_model, in_size, out_count):
    # find input size of model    
    batcmd = ('neuronrt -a %s -d' % dla_model)
    result = os.popen(batcmd).read()
    match = re.search('Handle = 0, <(\d+) x (\d+) x (\d+) x (\d+)>', result)
    if match:
        in_size = ( int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)) )
        return 1
    else:
        logging.error("FAIL to find input size of model")
        return 0
        
    # find output counts of model
    tmp = result.partition("Output")[2]
    match = re.findall('Handle = ', tmp)
    if match:
        out_count = len(match)
        return 1
    else:
        logging.error("FAIL to find output scountize of model")
        return 0

def benchmark_tflite_model_auto(model):
    tflite_target_list = [ ['mdla2.0', '', CLEAR_DIRTY], ['vpu', '', CLEAR_DIRTY] ]

    for element in tflite_target_list:
        target = element[0];
        
        element[1] = '%s, %s, %s' % (model, target, INIT_TIME)
        element[2] = CLEAR_DIRTY
        
        result = ''
        
        print("------------compile-----------------")
        dla = model.replace('.tflite', '.dla')
        tflite_2_dla(model, target, dla)
        if not os.path.exists(dla):
            logging.error("FAIL to convert model to dla with target %s, %s" % (target, model))
            continue

        result = ''
        
        print("------------Find input/output info-------------")
        # find input size and output count of model 
        intput_size = (-1,-1,-1,-1)
        output_count = 0
        batcmd = ('neuronrt -a %s -d' % dla)
        result = os.popen(batcmd).read()
        match = re.search('Handle = 0, <(\d+) x (\d+) x (\d+) x (\d+)>', result)
        if match:
            intput_size = ( int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)) )
        else:
            logging.error("FAIL to find input size of model")
            continue
            
        # find output counts of model
        tmp = result.partition("Output")[2]
        match = re.findall('Handle = ', tmp)
        if match:
            output_count = len(match)
        else:
            logging.error("FAIL to find output scountize of model")
            continue
        
        print("------------Gen input.bin----------------------")
        # gen rand input.bin
        intput_bin = 'input.bin'
        ndarray = np.random.randint(0, high=255, size=intput_size, dtype=np.uint8)
        ndarray.tofile(intput_bin)


        print("------------Inference--------------------------")
        # inference
        batcmd = 'neuronrt -m hw -a %s -c %s -b 100 -i %s ' % (dla, INFERENCE_CNT, intput_bin)
        for i in range(output_count):
            batcmd = batcmd + (' -o output_%s.bin ' % i)
        
        result = os.popen(batcmd).read()
        logging.debug(result)

        
        print("------------Avg inference time-----------------")
        # find 'Total inference time' in output log
        match = re.search('Total inference time = (\d+)', result)
        if match:
            time = float(match.group(1))
            # calculate avg inference time
            avg_time = time / INFERENCE_CNT
            element[1] = '%s, %s, %s %s' % (model, target, TIME, avg_time)
            element[2] = DIRTY;

        os.remove(dla)
        
    print("------------Summary--------------------------------")    
    # print model inference time by each target
    for element in tflite_target_list:
        if (element[2] == DIRTY):
            logging.info(element[1])
    print("---------------------------------------------------")     



def benchmark_tflite_model(model):    
    result = ''
        
    print("------------compile-----------------")
    dla = model.replace('.tflite', '.dla')
    tflite_2_dla(model, user_specific_target, dla)
    if not os.path.exists(dla):
        logging.error("FAIL to convert model to dla with target %s, %s" % (user_specific_target, model))
    return

    result = ''
        
    print("------------Find input/output info-------------")
    # find input size and output count of model 
    intput_size = (-1,-1,-1,-1)
    output_count = 0
    batcmd = ('neuronrt -a %s -d' % dla)
    result = os.popen(batcmd).read()
    match = re.search('Handle = 0, <(\d+) x (\d+) x (\d+) x (\d+)>', result)
    if match:
        intput_size = ( int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)) )
    else:
        logging.error("FAIL to find input size of model")
    return
            
    # find output counts of model
    tmp = result.partition("Output")[2]
    match = re.findall('Handle = ', tmp)
    if match:
        output_count = len(match)
    else:
        logging.error("FAIL to find output scountize of model")
    return
        
    print("------------Gen input.bin----------------------")
    # gen rand input.bin
    intput_bin = 'input.bin'
    ndarray = np.random.randint(0, high=255, size=intput_size, dtype=np.uint8)
    ndarray.tofile(intput_bin)


    print("------------Inference--------------------------")
    # inference
    batcmd = 'neuronrt -m hw -a %s -c %s -b 100 -i %s ' % (dla, INFERENCE_CNT, intput_bin)
    for i in range(output_count):
        batcmd = batcmd + (' -o output_%s.bin ' % i)
    
    result = os.popen(batcmd).read()
    logging.debug(result)

    os.remove(dla)
        
    print("------------Avg inference time-----------------")
    # find 'Total inference time' in output log
    match = re.search('Total inference time = (\d+)', result)
    if match:
        time = float(match.group(1))
        # calculate avg inference time
        avg_time = time / INFERENCE_CNT 
    else:
        logging.error("FAIL to find avg inference time of model")
        return

    print("------------Summary--------------------------------")    
    logging.info('%s, %s, avg inference time: %s' % (model, user_specific_target, avg_time))
    print("---------------------------------------------------")    




def benchmark_dla_model(model):

    print("------------Find input/output info-------------")
    # find input size and output count of model 
    intput_size = (-1,-1,-1,-1)
    output_count = 0
    batcmd = ('neuronrt -a %s -d' % model)
    result = os.popen(batcmd).read()
    match = re.search('Handle = 0, <(\d+) x (\d+) x (\d+) x (\d+)>', result)
    if match:
        intput_size = ( int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)) )
    else:
        logging.error("FAIL to find input size of model")
        return
        
    # find output counts of model
    tmp = result.partition("Output")[2]
    match = re.findall('Handle = ', tmp)
    if match:
        output_count = len(match)
    else:
        logging.error("FAIL to find output scountize of model")
        return
    
    print("------------Gen input.bin----------------------")
    # gen rand input.bin
    intput_bin = 'input.bin'
    ndarray = np.random.randint(0, high=255, size=intput_size, dtype=np.uint8)
    ndarray.tofile(intput_bin)


    print("------------Inference--------------------------")
    # inference
    batcmd = 'neuronrt -m hw -a %s -c %s -b 100 -i %s ' % (model, INFERENCE_CNT, intput_bin)
    for i in range(output_count):
        batcmd = batcmd + (' -o output_%s.bin ' % i)
    
    result = os.popen(batcmd).read()
    logging.debug(result)

    
    print("------------Avg inference time-----------------")
    # find 'Total inference time' in output log
    match = re.search('Total inference time = (\d+)', result)
    if match:
        time = float(match.group(1))
        # calculate avg inference time
        avg_time = time / INFERENCE_CNT 
    else:
        logging.error("FAIL to find avg inference time of model")
        return

    print("------------Summary--------------------------------")    
    logging.info('%s, avg inference time: %s' % (model, avg_time))
    print("---------------------------------------------------") 
        

if __name__ == "__main__":
    pwd = os. getcwd()
    
    # preapre log
    result_log = pwd + "/benchmark.log"
    if os.path.exists(result_log):
        os.remove(result_log)
        
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(result_log),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # parse input args.
    interactive_mode = 1
    if len(sys.argv) >= 2:
        if (ARG_AUTO_RUN == sys.argv[1]):
            interactive_mode = 0
    
    
    if not interactive_mode:
        # auto run, find all models in current folder and inference them one by one
        for file in os.listdir(pwd):
            if file.endswith('.tflite'):
                benchmark_tflite_model_auto(file)
    else:             
        # interactive mode, allow user to select model and target to inference
        user_specific_model = input('Enter one of following options to benchmark:\n - Enter tflite or dla model file\n - Enter "%s" to benchmark all tflite models in current folder\n ' % RUN_ALL)
        if (user_specific_model.lower() == RUN_ALL.lower()):
            # find all models in current folder and inference them one by one
            user_specific_target = input('Select a target to inference:\n - Enter "mdla2.0"\n - Enter "vpu"\n - Enter "tflite_cpu"\n ')
            for file in os.listdir(pwd):
                if file.endswith('.tflite'):
                    benchmark_tflite_model(file)
        else:
            # inference user specific model
            if os.path.exists(user_specific_model):
                if user_specific_model.endswith('.tflite'):
                    user_specific_target = input('Select a target to inference:\n - Enter "mdla2.0"\n - Enter "vpu"\n - Enter "tflite_cpu\n')
                    benchmark_tflite_model(user_specific_model)
                elif user_specific_model.endswith('.dla'):
                    benchmark_dla_model(user_specific_model)
            else:
                logging.error('model: %s not exist', user_specific_model)
            
        
    