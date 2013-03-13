import urlparse
import sys
import util
import json
import cgi
import multiprocessing
sys.path.append('../')
from util import BackgroundWorker
from urlparse import urlparse, parse_qs
import lib.config as global_config

# TO IMPLEMENT:
#     X ExecuteApexServlet
#     ApexUnitTestServlet
#     MetadataIndexServlet
#     X DeployServlet
#     ExistingProjectServlet
#     OrgConnectionServlet
#     MetadataListServlet
#     VersionControlServlet

# POST /project
# {
#     "project_name"  : "my project name"
#     "username"      : "mm@force.com",
#     "password"      : "force",
#     "org_type"      : "developer",
#     "vc_username"   : "",
#     "vc_password"   : "",
#     "vc_url"        : "",
#     "vc_type"       : "",
#     "vc_branch"     : "",
#     "package"       : {
#         "ApexClass"     : "*",
#         "ApexTrigger"   : ["Trigger1", "Trigger2"]
#     }
# }
def project_request(request_handler):
    request_id, tmp_directory = util.get_request_id_and_put_tmp_directory()
    params, raw_post_body = get_request_params(request_handler)
    worker = BackgroundWorker('new_project', params, True, request_id, tmp_directory, raw_post_body)
    p = multiprocessing.Process(target=process_request_in_background,args=(worker,)).start()
    return respond_with_async_request_id(request_handler, request_id)

# POST /project/edit
# body same as project_request
def project_edit_request(request_handler):
    request_id, tmp_directory = util.get_request_id_and_put_tmp_directory()
    params, raw_post_body = get_request_params(request_handler)
    worker = BackgroundWorker('edit_project', params, True, request_id, tmp_directory, raw_post_body)
    p = multiprocessing.Process(target=process_request_in_background,args=(worker,)).start()
    return respond_with_async_request_id(request_handler, request_id)

# GET /session?username=mm@force.com&password=force&org_type=developer
def get_active_session_request(request_handler):
    request_id, tmp_directory = util.get_request_id_and_put_tmp_directory()
    params, json_body = get_request_params(request_handler)
    worker = BackgroundWorker('get_active_session', params, False, request_id, tmp_directory, json_body)
    response = worker.run()
    respond(request_handler, response)

# POST /project/creds
# {
#     "project_name"  : "my project name"
#     "username"      : "mm@force.com",
#     "password"      : "force",
#     "org_type"      : "developer",
# }
# NOTE: project name should not be updated, as it is used to find the project in question
# TODO: maybe we assign a unique ID to each project which will give users the flexibility
#       to change the project name??
# TODO: we may need to implement a "clean" flag which will clean the project after creds
#       have been updated
def update_credentials_request(request_handler):
    request_id, tmp_directory = util.get_request_id_and_put_tmp_directory()
    params, raw_post_body = get_request_params(request_handler)
    worker = BackgroundWorker('update_credentials', params, False, request_id, tmp_directory, raw_post_body)
    response = worker.run()
    respond(request_handler, response)

# POST /apex/execute
# {
#     "project_name"    : "my project name"
#     "log_level"       : "DEBUG",
#     "log_category"    : "APEX_CODE",
#     "body"            : "String foo = 'bar';",
# }
def execute_apex_request(request_handler):
    request_id, tmp_directory = util.get_request_id_and_put_tmp_directory()
    params, raw_post_body = get_request_params(request_handler)
    worker = BackgroundWorker('execute_apex', params, True, request_id, tmp_directory, raw_post_body)
    p = multiprocessing.Process(target=process_request_in_background,args=(worker,)).start()
    return respond_with_async_request_id(request_handler, request_id)

# POST /project/deploy
# call to deploy metadata to a server
# {
#     "check_only"            : true,
#     "rollback_on_error"     : true,
#     "destinations"          : [
#         {
#             "username"              : "username1@force.com",
#             "org_type"              : "developer"
#         }
#     ],
#     "package"               : {
#         "ApexClass" : "*"
#     }
# }
def deploy_request(request_handler):
    request_id, tmp_directory = util.get_request_id_and_put_tmp_directory()
    params, raw_post_body = get_request_params(request_handler)
    worker = BackgroundWorker('deploy', params, True, request_id, tmp_directory, raw_post_body)
    p = multiprocessing.Process(target=process_request_in_background,args=(worker,)).start()
    return respond_with_async_request_id(request_handler, request_id)

# POST /project/unit_test
# {
#     "classes" : [
#         "UnitTestClass1", "UnitTestClass2"
#     ],
#     "run_all_tests" : false
# }
def unit_test_request(request_handler):
    request_id, tmp_directory = util.get_request_id_and_put_tmp_directory()
    params, raw_post_body = get_request_params(request_handler)
    worker = BackgroundWorker('unit_test', params, True, request_id, tmp_directory, raw_post_body)
    p = multiprocessing.Process(target=process_request_in_background,args=(worker,)).start()
    return respond_with_async_request_id(request_handler, request_id)

def connections_list_request(request_handler):
    request_id, tmp_directory = util.get_request_id_and_put_tmp_directory()
    params, raw_post_body = get_request_params(request_handler)
    worker = BackgroundWorker('list_connections', params, False, request_id, tmp_directory, raw_post_body)
    response = worker.run()
    respond(request_handler, response)

def connections_new_request(request_handler):
    request_id, tmp_directory = util.get_request_id_and_put_tmp_directory()
    params, raw_post_body = get_request_params(request_handler)
    worker = BackgroundWorker('new_connection', params, False, request_id, tmp_directory, raw_post_body)
    response = worker.run()
    respond(request_handler, response)

def connections_delete_request(request_handler):
    request_id, tmp_directory = util.get_request_id_and_put_tmp_directory()
    params, raw_post_body = get_request_params(request_handler)
    worker = BackgroundWorker('delete_connection', params, False, request_id, tmp_directory, raw_post_body)
    response = worker.run()
    respond(request_handler, response)

def auth_request(request_handler):
    request_id, tmp_directory = util.get_request_id_and_put_tmp_directory()
    params = get_request_params(request_handler)
    return respond_with_async_request_id(request_handler, request_id)

#call to get information about a particular SVN or Git repository
def version_control_request():
    params = get_request_params(request_handler)

# GET /metadata/list
# {
#     "sid"             : "",
#     "metadata_type"   : "",
#     "murl"            : ""
# }
#call to get a list of metadata of a certain type
def metadata_list_request(request_handler):
    request_id, tmp_directory = util.get_request_id_and_put_tmp_directory()
    params, json_body = get_request_params(request_handler)
    worker = BackgroundWorker('list_metadata', params, False, request_id, tmp_directory, json_body)
    response = worker.run()
    respond(request_handler, response)

#call to update the project .metadata index
def metadata_index_request(request_handler):
    request_id, tmp_directory = util.get_request_id_and_put_tmp_directory()
    params, raw_post_body = get_request_params(request_handler)
    worker = BackgroundWorker('index_metadata', params, True, request_id, tmp_directory, raw_post_body)
    p = multiprocessing.Process(target=process_request_in_background,args=(worker,)).start()
    return respond_with_async_request_id(request_handler, request_id)

#client polls this servlet to determine whether the request is done
#if the request IS done, it will respond with the body of the request
def status_request(request_handler):
    params, json_string = get_request_params(request_handler)
    try:
        request_id = params['id']
    except:
        request_id = params['id'][0]
    print '>>>>>> checking on request id ', request_id
    if util.response_ready(request_id) == True:
        response_body = util.get_request_response(request_id)
        print '>>>>>> response body: ', response_body
        respond(request_handler, response_body, 'text/json')
    else:
        print '>>>>>> request is not ready'
        respond_with_async_request_id(request_handler, request_id)

def get_raw_post_body(request_handler):
    return request_handler.rfile.read(int(request_handler.headers['Content-Length']))

def get_request_params(request_handler):
    print '>>>>>> ', request_handler.path
    print '>>>>>> ', request_handler.command
    #print '>>>>>> ', request_handler.headers
    if request_handler.command == 'POST':
        data_string = request_handler.rfile.read(int(request_handler.headers['Content-Length']))
        #print '>>>>>>> ', data_string
        postvars = json.loads(data_string)
        if 'package' in postvars:
            postvars['package'] = json.dumps(postvars['package'])
        return postvars, data_string
    elif request_handler.command == 'GET':
        params = parse_qs(urlparse(request_handler.path).query)
        for key in params:
            params[key] = params[key][0]
        json_string = json.dumps(params)
        return params, json_string

def respond_with_async_request_id(request_handler, request_id):
    response = { 'status' : 'pending', 'id' : request_id }
    json_response_body = json.dumps(response)
    respond(request_handler, json_response_body, 'text/json')

def respond(request_handler, body, type='text/json'):
    #print '>>>>>>>> responding with, ' body
    request_handler.send_response(200)
    request_handler.send_header('Content-type', type)
    request_handler.send_header('Access-Control-Allow-Origin', '*')
    request_handler.end_headers()
    request_handler.wfile.write(body)
    return

def process_request_in_background(worker):
    worker.run()

mappings = {
    '/status'               : { 'GET'   : status_request },     
    '/project'              : { 'POST'  : project_request }, 
    '/project/edit'         : { 'POST'  : project_edit_request }, 
    '/project/creds'        : { 'POST'  : update_credentials_request },
    '/project/deploy'       : { 'POST'  : deploy_request },
    '/project/unit_test'    : { 'POST'  : unit_test_request },
    '/project/index'        : { 'POST'  : metadata_index_request },
    '/project/conns/list'   : { 'GET'   : connections_list_request },
    '/project/conns/new'    : { 'POST'  : connections_new_request },
    '/project/conns/delete' : { 'POST'  : connections_delete_request },
    '/session'              : { 'GET'   : get_active_session_request },
    '/apex/execute'         : { 'POST'  : execute_apex_request },
    '/metadata/list'        : { 'GET'   : metadata_list_request }
    # '/project/existing'  : { 'GET'  : project_request }, 
    # '/vc'                : { 'GET'  : version_control_request }
}