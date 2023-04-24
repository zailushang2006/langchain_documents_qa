
from documents_qa import conversation_qa
# use falsk to build a web restful api
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_restful import reqparse
from config import Cfg

app = Flask(__name__)

def str_to_bool(str):
	return True if str.lower() == 'true' else False


# use reqparse to parse the request, args is query: str, chat_history: List[str], category: str, stream: bool = False
parser = reqparse.RequestParser()
parser.add_argument('query', type=str, required=True, help='query cannot be blank!')
# parser.add_argument('chat_history', type=str, action="append", required=True, help='chat_history cannot be blank!')
parser.add_argument('chat_history', type=list, location="json", required=True, help='chat_history cannot be blank!')
parser.add_argument('category', type=str, required=True, help='category cannot be blank!')
parser.add_argument('stream', type=str_to_bool, default=True, help='stream cannot be blank!')

# use flask_restful to build a restful api

class DocumentsQA(Resource):
    def get(self):

        return "please use post method to query the documents qa"

    def post(self):
        args = parser.parse_args()
        print("-- args: ", args)
        query = args.get('query')
        chat_history = args.get('chat_history', [])
        if chat_history:
            chat_history = [tuple(item) for item in chat_history]

        category = args.get('category')
        stream = args.get('stream', False)
        # if "stream" in args:
        #     stream = args.get('stream')
        #     stream = True if stream.lower() == 'true' else False
        # else:
        #     stream = False
        try:
            result = conversation_qa(query, chat_history, category, stream)
            return result
        except Exception as e:
            print("-- exception: ", e)
            return {
                        "question": query,
                        "chat_history": [],
                        "answer": "没有从文档中找到相关答案。"
                    }


api = Api(app)

# use flask_restful to add a resource
api.add_resource(DocumentsQA, '/documents_qa')


if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='0.0.0.0', port=Cfg.SERVER_PORT)

