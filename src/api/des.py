import requests
import sys 
import os
import time 
import json 
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='MapReduce inverted index (Problem 1)')
    parser.add_argument('-f', help='path to csv file', default='.')
    return parser.parse_args()

positions = '''
    RA,DEC,MAKE_FITS,COLORS_FITS,RGB_STIFF_COLORS,XSIZE,YSIZE
    16.3319,1.7490,true,,izy;grz,0.50,0.50
    '''

def get_username(path: str):
    """
    Returns the username to use in DESaccess.
    """
    return open(path, 'r').readlines()[0].replace('\n', '')


def get_password(path: str):
    """
    Returns the passwords to use in DESaccess
    """
    return open(path, 'r').readlines()[1]

CREDENTIALS_PATH = "../../../creds.txt"

# Credit https://github.com/des-labs/desaccess-docs/blob/master/_static/DESaccess_API_example.ipynb.

username = get_username(CREDENTIALS_PATH)
password = get_password(CREDENTIALS_PATH)
BASE_DOMAIN = 'des.ncsa.illinois.edu'
config = {
    'auth_token': '',
    'apiBaseUrl': 'https://{}/desaccess/api'.format(BASE_DOMAIN),
    'filesBaseUrl': 'https://{}/files-desaccess'.format(BASE_DOMAIN),
    'username': username,
    'password': password,
    'database': 'desdr',
    'release': 'dr2',
}

def login():
    """ 
    Obtains an auth token using the username and password credentials for a given database.
    Credit https://github.com/des-labs/desaccess-docs/blob/master/_static/DESaccess_API_example.ipynb
    """
    # Login to obtain an auth token
    r = requests.post(
        '{}/login'.format(config['apiBaseUrl']),
        data={
            'username': config['username'],
            'password': config['password'],
            'database': config['database']
        }
    )
    # Store the JWT auth token
    config['auth_token'] = r.json()['token']
    return config['auth_token']


def submit_cutout_job(data = {
        'db': config['database'],
        'release': config['release']
    }):
    """
    Submits a query job and returns the complete server response which includes the job ID.
    Credit https://github.com/des-labs/desaccess-docs/blob/master/_static/DESaccess_API_example.ipynb
    """

    # Submit job
    r = requests.put(
        '{}/job/cutout'.format(config['apiBaseUrl']),
        data=data,
        headers={'Authorization': 'Bearer {}'.format(config['auth_token'])}
    )
    response = r.json()
    # print(json.dumps(response, indent=2))
    
    if response['status'] == 'ok':
        job_id = response['jobid']
        print('Job "{}" submitted.'.format(job_id))
        # Refresh auth token
        config['auth_token'] = response['new_token']
    else:
        job_id = None
        print('Error submitting job: '.format(response['message']))
    
    return response


def submit_query_job(query):
    """
    Submits a query job and returns the complete server response which includes the job ID.
    Credit: https://github.com/des-labs/desaccess-docs/blob/master/_static/DESaccess_API_example.ipynb
    """

    # Specify API request parameters
    data = {
        'username': config['username'],
        'db': config['database'],
        'filename': 'results.csv',
        'query': query
    }

    # Submit job
    r = requests.put(
        '{}/job/query'.format(config['apiBaseUrl']),
        data=data,
        headers={'Authorization': 'Bearer {}'.format(config['auth_token'])}
    )
    response = r.json()
    
    if response['status'] == 'ok':
        job_id = response['jobid']
        print('Job "{}" submitted.'.format(job_id))
        # Refresh auth token
        config['auth_token'] = response['new_token']
    else:
        job_id = None
        print('Error submitting job: '.format(response['message']))
    
    return response


def get_job_status(job_id):
    """
    Returns the current status of the job identified by the unique job_id.
    Credit https://github.com/des-labs/desaccess-docs/blob/master/_static/DESaccess_API_example.ipynb
    """

    r = requests.post(
        '{}/job/status'.format(config['apiBaseUrl']),
        data={
            'job-id': job_id
        },
        headers={'Authorization': 'Bearer {}'.format(config['auth_token'])}
    )
    response = r.json()
    # Refresh auth token
    config['auth_token'] = response['new_token']
    # print(json.dumps(response, indent=2))
    return response


def download_job_files(url, outdir, fits_only=True):
    """
    Credit https://github.com/des-labs/desaccess-docs/blob/master/_static/DESaccess_API_example.ipynb
    """
    os.makedirs(outdir, exist_ok=True)
    r = requests.get('{}/json'.format(url))
    for item in r.json():
        if item['type'] == 'directory':
            suburl = '{}/{}'.format(url, item['name'])
            subdir = '{}/{}'.format(outdir, item['name'])
            download_job_files(suburl, subdir)
        elif item['type'] == 'file':
            if item['name'].split('.')[-1] == 'fits' or not(fits_only): 
                data = requests.get('{}/{}'.format(url, item['name']))
                with open('{}/{}'.format(outdir, item['name']), "wb") as file:
                    file.write(data.content)

    response = r.json()
    return response


def list_job_files(url, outdir):
    """
    Credit https://github.com/des-labs/desaccess-docs/blob/master/_static/DESaccess_API_example.ipynb
    """
    r = requests.get('{}/json'.format(url))
    for item in r.json():
        if item['type'] == 'directory':
            suburl = '{}/{}'.format(url, item['name'])
            subdir = '{}/{}'.format(outdir, item['name'])
            list_job_files(suburl, subdir)
        elif item['type'] == 'file':
            print('{}/{}'.format(url, item['name']))
    response = r.json()
    return response


def list_downloaded_files(download_dir):
    """
    Credit https://github.com/des-labs/desaccess-docs/blob/master/_static/DESaccess_API_example.ipynb
    """
    for dirpath, dirnames, filenames in os.walk(download_dir):
        for filename in filenames:
            print(os.path.join(dirpath, filename))


def list_downloaded_files(download_dir):
    """
    Credit https://github.com/des-labs/desaccess-docs/blob/master/_static/DESaccess_API_example.ipynb
    """
    for dirpath, dirnames, filenames in os.walk(download_dir):
        for filename in filenames:
            print(os.path.join(dirpath, filename))


def job_status_poll(job_id):
    """
    Credit https://github.com/des-labs/desaccess-docs/blob/master/_static/DESaccess_API_example.ipynb
    """
    print('Polling status of job "{}"...'.format(job_id), end='')
    job_status = ''
    response = None
    while job_status != 'ok':
        # Fetch the current job status
        response = get_job_status(job_id)
        # Quit polling if there is an error getting a status update
        if response['status'] != 'ok':
            break
        job_status = response['jobs'][0]['job_status']
        if job_status == 'success' or job_status == 'failure':
            print('\nJob completed with status: {}'.format(job_status))
            break
        else:
            # Display another dot to indicate that polling is still active
            print('.', end='', sep='', flush=True)
        time.sleep(3)
    return response


def get_fits_cutouts(positions: str, output_dir: str, query=None):
    # Authenticate and store the auth token for subsequent API calls
    # Credit https://github.com/des-labs/desaccess-docs/blob/master/_static/DESaccess_API_example.ipynb
    try:
        print('Logging in as user "{}" ("{}") and storing auth token...'.format(config['username'], config['database']))
        login()
    except:
        print('Login failed.')
        sys.exit(1)

    if query:
        job_type = 'query'

        # Optional, submit query. 
        print('Submitting query job...')
        response = submit_query_job()


        # Store the unique job ID for the new job
        job_id = response['jobid']
        print('New job submitted: {}'.format(job_id))

        response = job_status_poll(job_id)

        # If successful, display job results
        if response['status'] == 'ok':
            job_type = response['jobs'][0]['job_type']
            job_id = response['jobs'][0]['job_id']
            # Construct the job file download URL
            job_url = '{}/{}/{}/{}'.format(config['filesBaseUrl'], config['username'], job_type, job_id)
            download_dir = '../../data/DES-outputs/{}'.format(job_id)
            # Download each raw job file sequentially to a subfolder of the working directory
            download_job_files(job_url, download_dir)
            print('Files for job "{}" downloaded to "{}"'.format(job_id, download_dir))
            list_downloaded_files(download_dir)
        else:
            print('The job "{}" failed.'.format(job_id))

    # Set up cutout job, submit.
    job_type = 'cutout'
    data = {
            'db': config['database'],
            'release': config['release'],
            'positions': positions,
        }
    print('Submitting cutout job...')
    response = submit_cutout_job(data=data)

    if response['status'] == 'ok':
        # Store the unique job ID for the new job
        job_id = response['jobid']
        print('New job submitted: {}'.format(job_id))
        response = job_status_poll(job_id)
        print(json.dumps(response, indent=2))
    else:
        print('Response: {}'.format(json.dumps(response, indent=2)))

    # If successful, display job results
    if response['status'] == 'ok':
        job_type = response['jobs'][0]['job_type']
        job_id = response['jobs'][0]['job_id']
        # Construct the job file download URL
        job_url = '{}/{}/{}/{}'.format(config['filesBaseUrl'], config['username'], job_type, job_id)
        download_dir = '../../data/DES-outputs/{}'.format(job_id)
        # Download each raw job file sequentially to a subfolder of the working directory
        download_job_files(job_url, download_dir)
        print('Files for job "{}" downloaded to "{}"'.format(job_id, download_dir))
        list_downloaded_files(download_dir)
    else:
        print('The job "{}" failed.'.format(job_id))


if __name__ == '__main__':
    args = parse_args()
    with open(args.f) as f:
        file_text = f.readlines()
        positions = ''
        for string in file_text:
            positions += string

        get_fits_cutouts(positions, 'foo')