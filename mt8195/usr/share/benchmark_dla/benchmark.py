import argparse
import os
import sys
import re
import numpy as np
import logging

available_backends = ['mdla2.0', 'vpu', 'tflite_cpu']

DIRTY = 1
CLEAR_DIRTY = 0

TIME = 'avg inference time:'
INIT_TIME = TIME + ' FAILED'

def PRINT_LOG(msg, enable):
    if enable:
        print(msg)

def tflite_2_dla(tflite_model, target, dla_model):
    # compile for specific target
    if os.path.exists(dla_model):
        return

    batcmd = ('ncc-tflite -arch %s %s -o %s' % (target, tflite_model, dla_model) )
    result = os.popen(batcmd).read()
    logging.debug(result)

def benchmark_tflite_model_auto(model, count=100, verbose=False, cache_dla=False):
    tflite_target_list = [ ['mdla2.0', '', CLEAR_DIRTY], ['vpu', '', CLEAR_DIRTY] ]

    for element in tflite_target_list:
        target = element[0];

        element[1] = '%s, %s, %s' % (model, target, INIT_TIME)
        element[2] = CLEAR_DIRTY

        result = ''

        PRINT_LOG("\n[Inference Model:%s on Target:%s, %d times]" % (model, target, count), verbose)
        PRINT_LOG("\n------------Compile model----------------------", verbose)
        
        dla = model.replace('.tflite', "-"+ target + '.dla')
        tflite_2_dla(model, target, dla)
        if not os.path.exists(dla):
            logging.error("FAIL to convert model to dla with target %s, %s" % (target, model))
            continue

        result = ''


        PRINT_LOG("\n------------Find input/output info-------------", verbose)
            
        # find input size and output count of model
        intput_size = (-1,-1,-1,-1)
        output_count = 0
        batcmd = ('ncc-tflite --show-io-info %s' % model )
        result = os.popen(batcmd).read()
        logging.debug(result)

        match = re.search('of output tensors: (\d+)', result)
        if match:
            output_count = int(match.group(1))
        else:
            logging.error("FAIL to find output count of model")
            continue

        tmp = result.partition("# of output tensors")[0]
        match = re.search('Shape: {(\d+),(\d+),(\d+),(\d+)}', tmp)
        if match:
            intput_size = ( int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)) )
        else:
            logging.error("FAIL to find input size of model")
            continue

        result = ''


        PRINT_LOG("\n------------Gen input.bin----------------------", verbose)

        # gen rand input.bin
        intput_bin = 'input.bin'
        ndarray = np.random.randint(0, high=255, size=intput_size, dtype=np.uint8)
        ndarray.tofile(intput_bin)


        PRINT_LOG("\n------------Inference--------------------------", verbose)

        # inference
        batcmd = 'neuronrt -m hw -a %s -c %s -b 100 -i %s ' % (dla, count, intput_bin)
        for i in range(output_count):
            batcmd = batcmd + (' -o output_%s.bin ' % i)

        result = os.popen(batcmd).read()
        logging.debug(result)


        PRINT_LOG("\n------------Avg inference time-----------------", verbose)

        # find 'Total inference time' in output log
        match = re.search('Total inference time = (\d+)', result)
        if match:
            time = float(match.group(1))
            # calculate avg inference time
            avg_time = time / count
            element[1] = '%s, %s, %s %s' % (model, target, TIME, avg_time)
            element[2] = DIRTY;

        if not cache_dla:
            os.remove(dla)

    PRINT_LOG("\n------------Summary----------------------------", verbose)

    # print model inference time by each target
    for element in tflite_target_list:
        if (element[2] == DIRTY):
            logging.info(element[1])



def benchmark_tflite_model(model, target="mdla2.0", count=100, verbose=False, cache_dla=False):
    result = ''

    PRINT_LOG("\n[Inference Model:%s on Target:%s, %d times]" % (model, target, count), verbose)
    PRINT_LOG("\n------------Compile model----------------------", verbose)

    dla = model.replace('.tflite', "-"+ target + '.dla')
    tflite_2_dla(model, target, dla)
    if not os.path.exists(dla):
        logging.error("FAIL to convert model to dla with target %s, %s" % (target, model))
        return

    result = ''


    PRINT_LOG("\n------------Find input/output info-------------", verbose)

    # find input size and output count of model
    intput_size = (-1,-1,-1,-1)
    output_count = 0
    batcmd = ('ncc-tflite --show-io-info %s' % model )
    result = os.popen(batcmd).read()
    logging.debug(result)

    match = re.search('of output tensors: (\d+)', result)
    if match:
        output_count = int(match.group(1))
    else:
        logging.error("FAIL to find output count of model")
        return

    tmp = result.partition("# of output tensors")[0]
    match = re.search('Shape: {(\d+),(\d+),(\d+),(\d+)}', tmp)
    if match:
        intput_size = ( int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)) )
    else:
        logging.error("FAIL to find input size of model")
        return

    result = ''

    PRINT_LOG("\n------------Gen input.bin----------------------", verbose)

    # gen rand input.bin
    intput_bin = 'input.bin'
    ndarray = np.random.randint(0, high=255, size=intput_size, dtype=np.uint8)
    ndarray.tofile(intput_bin)



    PRINT_LOG("\n------------Inference--------------------------", verbose)

    # inference
    batcmd = 'neuronrt -m hw -a %s -c %s -b 100 -i %s ' % (dla, count, intput_bin)
    for i in range(output_count):
        batcmd = batcmd + (' -o output_%s.bin ' % i)

    result = os.popen(batcmd).read()
    logging.debug(result)

    if not cache_dla:
        os.remove(dla)


    PRINT_LOG("\n------------Avg inference time-----------------", verbose)

    # find 'Total inference time' in output log
    match = re.search('Total inference time = (\d+)', result)
    if match:
        time = float(match.group(1))
        # calculate avg inference time
        avg_time = time / count
    else:
        logging.error("FAIL to find avg inference time of model")
        return


    PRINT_LOG("\n------------Summary----------------------------", verbose)

    logging.info('%s, %s, avg inference time: %s' % (model, target, avg_time))



def benchmark_dla_model(model, count=100, verbose=False):

    PRINT_LOG("\n[Inference Model:%s, %d times]" % (model, count), verbose)
    PRINT_LOG("\n------------Find input/output info-------------", verbose)

    # find input size and output count of model
    intput_size = (-1,-1,-1,-1)
    output_count = 0
    batcmd = ('neuronrt -a %s -d' % model)
    result = os.popen(batcmd).read()
    match = re.search('Handle = 0, <(\d+) x (\d+) x (\d+) x (\d+)>', result)
    if match:
        PRINT_LOG("\n^^^^^^ Ignore above error msg because this step queries input/output info from model, not inference model ", True)
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


    PRINT_LOG("\n------------Gen input.bin----------------------", verbose)

    # gen rand input.bin
    intput_bin = 'input.bin'
    ndarray = np.random.randint(0, high=255, size=intput_size, dtype=np.uint8)
    ndarray.tofile(intput_bin)



    PRINT_LOG("\n------------Inference--------------------------", verbose)

    # inference
    batcmd = 'neuronrt -m hw -a %s -c %s -b 100 -i %s ' % (model, count, intput_bin)
    for i in range(output_count):
        batcmd = batcmd + (' -o output_%s.bin ' % i)

    result = os.popen(batcmd).read()
    logging.debug(result)


    PRINT_LOG("\n------------Avg inference time-----------------", verbose)

    # find 'Total inference time' in output log
    match = re.search('Total inference time = (\d+)', result)
    if match:
        time = float(match.group(1))
        # calculate avg inference time
        avg_time = time / count
    else:
        logging.error("FAIL to find avg inference time of model")
        return


    PRINT_LOG("\n------------Summary--------------------------------", verbose)

    logging.info('%s, avg inference time: %s' % (model, avg_time))




# argument parser
parser = argparse.ArgumentParser()

parser.add_argument(
        '--auto',
		action='store_true',
		help='Auto run, find all models in current folder and inference them one by one. It will ignore options: --file, --dla and --target')

parser.add_argument(
        '--stress',
		action='store_true',
		help='Stress test, find all models in current folder and inference them one by one. It will ignore options: --auto, --file, --dla and --target')

parser.add_argument(
        '--file',
		default=None,
		help='Input a tflite model to inference. it will be executed with option: --target')

parser.add_argument(
        '--target',
        default="mdla2.0",
		choices=available_backends,
		help='Choose a backends to inference. Default: mdla2.0')

parser.add_argument(
        '--dla',
		default=None,
		help='Input a dla file to inference. It will ignore option: --target')

parser.add_argument(
        '--count',
        default=100,
		type=int,
		help='How many times of inference. Default: 100')

parser.add_argument(
        '--quit',
		action='store_true',
		help='print a summary only on inference complete')

args = parser.parse_args()


pwd = os. getcwd()


# preapre log
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

if args.stress is False:
    sh = logging.FileHandler(pwd + "/benchmark.log", mode='w')
    fh = logging.StreamHandler(sys.stdout)
    logging.getLogger('').addHandler(sh)
    logging.getLogger('').addHandler(fh)

verbose = not args.quit

if args.auto is True or args.stress is True:
    cache_dla = False
    if args.stress is True:
        cache_dla = True
        verbose = False
        
    # auto run, find all models in current folder and inference them one by one
    for file in os.listdir(pwd):
        if file.endswith('.tflite'):
            benchmark_tflite_model_auto(file, args.count, verbose, cache_dla)

else:
    if os.path.exists(args.file):
        if args.file.endswith('.tflite'):
            benchmark_tflite_model(args.file, args.target, args.count, verbose, False)
        elif args.file.endswith('.dla'):
            benchmark_dla_model(args.file, args.count, verbose)
    else:
        logging.error('Error to load model %s', args.file)
