import os,sys,json,argparse
import datetime
import time
PATH = '/home/soporte/Documents/EVENTO'
wr_path1 = '/home/soporte/Documents/PDATA/PDATA_C0'
wr_path2 = '/home/soporte/Documents/PDATA/PDATA_CC16'

def max_index(r, sample_rate, ipp):

    return int(sample_rate*ipp*1e6 * r / 60) + int(sample_rate*ipp*1e6 * 1.2 / 60)


def main(args):

    experiment = args.experiment
    fp = open(os.path.join(PATH, experiment, 'experiment.conf'))
    conf = json.loads(fp.read())

    ipp_km = conf['usrp_tx']['ipp']
    ipp = ipp_km * 2 /300000
    sample_rate  = conf['usrp_rx']['sample_rate']
    axis = ['0' if x=='elevation' else '1' for x in conf['pedestal']['axis']]      # AZIMUTH 1 ELEVACION 0
    speed_axis = conf['pedestal']['speed']
    steps = conf['pedestal']['table']
    time_offset = args.time_offset
    parameters = args.parameters
    start_date = experiment.split('@')[1].split('T')[0].replace('-', '/')
    end_date = start_date
    if args.start_time:
        start_time = args.start_time
    else:
        start_time = experiment.split('@')[1].split('T')[1].replace('-', ':')
    #start_time = '16:15:00'
    end_time = '23:59:59'
    N = int(1/(speed_axis[0]*ipp))                                               # 1 GRADO DE RESOLUCION
    path = os.path.join(PATH, experiment, 'rawdata')
    path_ped = os.path.join(PATH, experiment, 'position')
    path_plots = os.path.join(PATH, experiment, 'plotsC0_PM_R'+str(args.range)+'km')
    path_save = os.path.join(PATH, experiment, 'paramC0_PM_R'+str(args.range)+'km_1.62km')
    RMIX = 1.62

    from schainpy.controller import Project

    project = Project()
    project.setup(id='1', name='Sophy', description='sophy proc')

    reader = project.addReadUnit(datatype='DigitalRFReader',
        path=path,
        startDate=start_date,
        endDate=end_date,
        startTime=start_time,
        endTime=end_time,
        delay=30,
        online=args.online,
        walk=1,
        ippKm = ipp_km,
        getByBlock = 1,
        nProfileBlocks = N,
    )

    if not conf['usrp_tx']['enable_2']: # One Pulse
        voltage = project.addProcUnit(datatype='VoltageProc', inputId=reader.getId())

        if conf['usrp_tx']['code_type_1'] != 'None':
            codes = [ c.strip() for c in conf['usrp_tx']['code_1'].split(',')]
            code = []
            for c in codes:
                code.append([int(x) for x in c])
            op = voltage.addOperation(name='Decoder', optype='other')
            op.addParameter(name='code', value=code)
            op.addParameter(name='nCode', value=len(code), format='int')
            op.addParameter(name='nBaud', value=len(code[0]), format='int')

        op = voltage.addOperation(name='setH0')
        op.addParameter(name='h0', value='-1.2')

        if args.range > 0:
            op = voltage.addOperation(name='selectHeights')
            op.addParameter(name='minIndex', value='0', format='int')
            op.addParameter(name='maxIndex', value=max_index(args.range, sample_rate, ipp), format='int')

    else: #Two pulses
        #------------VOLTAGE 1 **  UP-1------------------------------------------------------
        voltage1 = project.addProcUnit(datatype='VoltageProc', inputId=reader.getId())

        op = voltage1.addOperation(name='ProfileSelector')
        op.addParameter(name='profileRangeList', value='0,{}'.format(conf['usrp_tx']['repetitions_1']-1))

        if conf['usrp_tx']['code_type_1'] != 'None':
            codes = [ c.strip() for c in conf['usrp_tx']['code_1'].split(',')]
            code = []
            for c in codes:
                code.append([int(x) for x in c])
            op = voltage1.addOperation(name='Decoder', optype='other')
            op.addParameter(name='code', value=code)
            op.addParameter(name='nCode', value=len(code), format='int')
            op.addParameter(name='nBaud', value=len(code[0]), format='int')
        else:
            code=[[1]]

        # ojo con las Integraciones Coherentes
        #op = voltage1.addOperation(name='CohInt', optype='other') #Minimo integrar 2 perfiles por ser codigo complementario
        #op.addParameter(name='n', value=2, format='int')

        op = voltage1.addOperation(name='setH0')
        op.addParameter(name='h0', value='-1.68')

        if args.range > 0:
            op = voltage1.addOperation(name='selectHeights')
            op.addParameter(name='minIndex', value='0', format='int')
            op.addParameter(name='maxIndex', value=max_index(RMIX, sample_rate, ipp), format='int')
        # Numero de punto en FFT , si tomamos integraciones coherentes  2, deberia ser entre
        n = int(conf['usrp_tx']['repetitions_1'])#/2
        print ( " N show he n parameter",n )

        spec1= project.addProcUnit(datatype='SpectraProc', inputId=voltage1.getId())
        spec1.addParameter(name='nFFTPoints', value=n, format='int')
        spec1.addParameter(name='nProfiles' , value=n, format='int')

        opObj11 = spec1.addOperation(name='SpectraWriter', optype='other')
        opObj11.addParameter(name='path', value=wr_path1)
        opObj11.addParameter(name='blocksPerFile', value='360', format='int')

        #------------VOLTAGE 2 *****  UP-2 ------------------------------------------------------
        voltage2 = project.addProcUnit(datatype='VoltageProc', inputId=reader.getId())

        op = voltage2.addOperation(name='ProfileSelector')
        op.addParameter(name='profileRangeList', value='{},{}'.format(conf['usrp_tx']['repetitions_1'], conf['usrp_tx']['repetitions_1']+conf['usrp_tx']['repetitions_2']-1))


        if conf['usrp_tx']['code_type_2']:
            codes = [ c.strip() for c in conf['usrp_tx']['code_2'].split(',')]
            code = []
            for c in codes:
                code.append([int(x) for x in c])
            op = voltage2.addOperation(name='Decoder', optype='other')
            op.addParameter(name='code', value=code)
            op.addParameter(name='nCode', value=len(code), format='int')
            op.addParameter(name='nBaud', value=len(code[0]), format='int')

            op = voltage2.addOperation(name='CohInt', optype='other') #Minimo integrar 2 perfiles por ser codigo complementario
            op.addParameter(name='n', value=len(code), format='int')
            ncode = len(code)
        else:
            ncode = 1

        op = voltage2.addOperation(name='setH0')
        op.addParameter(name='h0', value='-1.68')

        if args.range > 0:
            op = voltage2.addOperation(name='selectHeights')
            op.addParameter(name='minIndex', value=max_index(RMIX, sample_rate, ipp), format='int')
            op.addParameter(name='maxIndex', value=max_index(args.range, sample_rate, ipp), format='int')
        # Numero de punto en FFT , si tomamos integraciones coherentes  2, deberia ser entre
        n2 = int(conf['usrp_tx']['repetitions_2'])/2
        print ( " N show he n parameter",n2 )

        spec2 = project.addProcUnit(datatype='SpectraProc', inputId=voltage2.getId())
        spec2.addParameter(name='nFFTPoints', value=n2, format='int')
        spec2.addParameter(name='nProfiles' , value=n2, format='int')

        opObj11 = spec2.addOperation(name='SpectraWriter', optype='other')
        opObj11.addParameter(name='path', value=wr_path2)
        opObj11.addParameter(name='blocksPerFile', value='360', format='int')


        #proc= project.addProcUnit(datatype='ParametersProc',inputId=spec2.getId())



    project.start()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Script to process SOPHy data.')
    parser.add_argument('experiment',
                        help='Experiment name')
    parser.add_argument('--parameters', nargs='*', default=['P'],
                        help='Variables to process: P, Z, V')
    parser.add_argument('--time_offset', default=0,
                        help='Fix time offset')
    parser.add_argument('--range', default=0, type=float,
                        help='Max range to plot')
    parser.add_argument('--save', action='store_true',
                        help='Create output files')
    parser.add_argument('--show', action='store_true',
                        help='Show matplotlib plot.')
    parser.add_argument('--online', action='store_true',
                        help='Set online mode.')
    parser.add_argument('--start_time', default='',
                        help='Set start time.')

    args = parser.parse_args()

    main(args)
