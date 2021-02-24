import executor_utils as eu
import json
from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)

@app.route('/build_and_run', methods=['POST'])
@cross_origin()
def build_and_run():
    data = json.loads(request.data)
    result = -1
    if 'code' not in data or 'lang' not in data:
        return 'You should provide both "code" and "lang"'


    code = data['code']
    lang = data['lang']
    input = data['input']
    # print('API got called with code: {} in {}'.format(code, lang))
    if lang == "python" :
        result = eu.build_and_run_no_build(code,input)
    elif lang == "c_gcc" \
        or lang == "cpp_g_plus_plus"\
        or lang == "java8"\
        or lang == "c_clang"\
        or lang == "cpp_clang":
        result = eu.build_and_run_build_needed(code,lang,input)
    return jsonify(result)

if __name__ == '__main__':
    # eu.load_image()
    app.run(debug=False,use_reloader=False)
