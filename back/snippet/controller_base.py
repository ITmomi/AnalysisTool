import logging
from flask import request, Response
from flask_restx import Resource, Namespace, fields

from config import app_config
from common.utils.response import make_json_response

logger = logging.getLogger(app_config.LOG)

NAME = Namespace(name='NAME', description='description')

name_response = NAME.model('name_response', {
    'version': fields.String(description='description', example='example')
})


@NAME.route('/uri/<int:id>')
@NAME.param('id', 'description')
class SETTINGConnectionCheck(Resource):
    parser = NAME.parser()
    parser.add_argument('argument', required=True, help='description')

    @NAME.expect(parser)
    @NAME.doc(model=name_response)
    @NAME.response(200, 'Success')
    @NAME.response(400, 'Bad Request')
    def post(self, id):
        """
        comment
        """
        logger.info(str(request))

        args = self.parser.parse_args()

        resp_form = None

        if resp_form.res:
            return make_json_response(data=resp_form.data)
        else:
            return Response(status=400)
