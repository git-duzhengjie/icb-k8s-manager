# coding:utf-8
# python version:
# author: duzhengjie
# date: 2018/5/3 11:36
# description:管理k8s
# ©成都爱车宝信息科技有限公司版权所有
import os
import subprocess
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import yaml
from tornado.options import define, options

define("port", default=8088, help="run on the given port", type=int)


def get_env():
    with open('k8s-deployment/yaml/icb-deployment/micro-main-deployment.yaml') as f:
        yl = yaml.load(f)
        return yl.get('spec').get('template').get('spec').get('containers')[0].get('env')[0].get('value')


def get_current_version():
    with open('version') as f:
        return f.read().strip()


class IndexHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        if args[0] == 'update':
            version = self.get_argument("version")
            current_version = get_current_version()
            if version != current_version:
                return_code = subprocess.call("sh k8s-deployment/update.sh -v " + version, shell=True)
                if return_code == 0:
                    with open("version", 'w') as f:
                        f.write(version)
                    subprocess.call("sed -i s/{0}/{1}/g k8s-deployment/yaml/icb-deployment/*"
                                    .format(current_version, version), shell=True)
                    self.write("{\"message\": \"成功\" }")
                else:
                    self.write("{\"message\": \"失败\" }")
            else:
                self.write("{\"message\": \"当前运行环境已经是该版本\" }")
        if args[0] == 'env/update':
            env = self.get_argument("ACB_MODE")
            current_env = get_env()
            if env == current_env:
                self.write("{\"message\": \"当前环境变量与要修改的一致\"}")
            else:
                return_code = subprocess.call("sh k8s-deployment/update.sh -o " + current_env + " -e " + env, shell=True)
                if return_code == 0:
                    self.write("{\"message\": \"成功\" }")
                else:
                    self.write("{\"message\": \"失败\" }")
        if args[0] == 'env':
            self.write(get_env())
        if args[0] == 'version':
            self.write(get_current_version())


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[(r'/(.*)', IndexHandler)],
        static_path=os.path.join(os.path.dirname(__file__), "k8s-deployment"),
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    print("listening on " + str(options.port))
    tornado.ioloop.IOLoop.instance().start()
