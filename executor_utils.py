import docker
from docker.errors import *
import uuid
import os
import shutil
import json

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
TEMP_BUILD_DIR = '{}/tmp'.format(CURRENT_DIR)


data = json.load(open("command.json","r"))
client = docker.from_env()

def make_dir(dir):
    try:
        os.mkdir(dir)
        print('Temp build directory [{}] created.'.format(dir))
    except OSError:
        print('Temp build directory [{}] exists.'.format(dir))



def build_and_run_no_build(code,input=""):
    result = {'build': None, 'run': None}

    source_file_parent_dir_name = uuid.uuid4()
    source_file_host_dir = '{}/{}'.format(TEMP_BUILD_DIR, source_file_parent_dir_name)
    source_file_guest_dir = '/test/{}'.format(source_file_parent_dir_name)
    make_dir(source_file_host_dir)


    with open('{}/{}'.format(source_file_host_dir, data['python3']['source_filename']), 'w') as source_file:
        source_file.write(code)
    
    with open('{}/{}'.format(source_file_host_dir, "input"), 'w') as source_file2:
        source_file2.write(input)

    try:
        log = client.containers.run(
            image=data['python3']['image_id'],
            command=data['python3']['execute_command'],
            volumes={source_file_host_dir: {'bind': source_file_guest_dir, 'mode': 'rw'}},
            working_dir=source_file_guest_dir,
            remove=True,
            mem_limit="50m")
        
        result['build'] = 'OK'
        result['run'] = log.decode('utf-8')

    except ContainerError as e:
        result['build'] = "ERROR"
        result['run'] = e.stderr.decode('utf-8')
        shutil.rmtree(source_file_host_dir)
        return result

    shutil.rmtree(source_file_host_dir)
    return result


def build_and_run_build_needed(code,lang,input = ""):
    result = {'build': None, 'run': None}

    source_file_parent_dir_name = uuid.uuid4()
    source_file_host_dir = '{}/{}'.format(TEMP_BUILD_DIR, source_file_parent_dir_name)
    source_file_guest_dir = '/test/{}'.format(source_file_parent_dir_name)
    make_dir(source_file_host_dir)


    with open('{}/{}'.format(source_file_host_dir, data[lang]['source_filename']), 'w') as source_file:
        source_file.write(code)
    with open('{}/{}'.format(source_file_host_dir, "input"), 'w') as source_file2:
        source_file2.write(input)

    try:
        log = client.containers.run(
            image=data[lang]['image_id'],
            command=data[lang]['build_command'],
            volumes={source_file_host_dir: {'bind': source_file_guest_dir, 'mode': 'rw'}},
            working_dir=source_file_guest_dir,
            remove=True,
            mem_limit="50m")
        
        result['build'] = 'Compilation Successful'
        result['run'] = log.decode('utf-8')

    except ContainerError as e:
        print('Build failed.')
        result['build'] = "Compilation Error"
        result['run'] = e.stderr.decode('utf-8')
        shutil.rmtree(source_file_host_dir)
        return result


    try:
        log = client.containers.run(
            image=data[lang]['image_id'],
            command=data[lang]['execute_command'],
            volumes={source_file_host_dir: {'bind': source_file_guest_dir, 'mode': 'rw'}},
            working_dir=source_file_guest_dir,
            remove=True,
            mem_limit="50m")
    
        result['build'] = 'Execution Successful'
        result['run'] = log.decode('utf-8')

    except ContainerError as e:
        result['build'] = "Execution Error"
        result['run'] = e.stderr.decode('utf-8')
        shutil.rmtree(source_file_host_dir)
        return result

    shutil.rmtree(source_file_host_dir)
    return result