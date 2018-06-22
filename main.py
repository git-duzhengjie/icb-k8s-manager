# coding:utf-8
# python version.json:
# author: duzhengjie
# date: 2018/5/3 11:36
# description:管理k8s
# ©成都爱车宝信息科技有限公司版权所有
import json
import os
import subprocess

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import yaml
from tornado.options import define, options

define("port", default=8088, help="run on the given port", type=int)
define("image_url", default="192.168.0.230:5000", help="image url", type=str)
message_success = "{\"message\": \"成功\" }"
message_failed = "{\"message\": \"失败\" }"


def get_env():
    with open('k8s-deployment/yaml/icb-deployment/micro-main-deployment.yaml') as f:
        yl = yaml.load(f)
        return yl.get('spec').get('template').get('spec').get('containers')[0].get('env')[0].get('value')


def get_current_version():
    with open('version.json') as f:
        return json.load(f)


def save_current_version(current_version):
    with open('version.json', 'w') as f:
        json.dump(current_version, f)


class IndexHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        if args[0] == 'update':
            image_name = self.get_argument("image_name", None)
            version = self.get_argument("version")
            service_name = self.get_argument("service_name")
            if image_name is None:
                image_name = service_name
            current_version = get_current_version()
            if version != current_version.get(service_name):
                command = "kubectl set image deployment {0} {0}={1}/{2}:{3} -n icb " \
                          "&& docker service update --image={1}/{2}:{3} {0} " \
                          "&& docker rm $(docker ps -qa) && docker rmi $(docker images -q)" \
                    .format(service_name, options.image_url, image_name, version)
                print(command)
                return_code = subprocess.call(command, shell=True)
                if return_code == 0:
                    current_version[service_name] = version
                    save_current_version(current_version)
                    self.write(message_success)
                else:
                    self.write(message_failed)
            else:
                command = "kubectl delete rs -l app={0} -n icb " \
                          "&& docker service update --image={1}/{2}:{3} {0} " \
                          "&& docker rm $(docker ps -qa) && docker rmi $(docker images -q)"\
                    .format(service_name, options.image_url, image_name, version)
                print(command)
                return_code = subprocess.call(command, shell=True)
                if return_code == 0:
                    self.write(message_success)
                else:
                    self.write(message_failed)
        if args[0] == 'env/update':
            env = self.get_argument("ACB_MODE")
            current_env = get_env()
            if env == current_env:
                self.write("{\"message\": \"当前环境变量与要修改的一致\"}")
            else:
                return_code = subprocess.call("sh k8s-deployment/update.sh -o " + current_env + " -e " + env,
                                              shell=True)
                if return_code == 0:
                    self.write(message_success)
                else:
                    self.write(message_failed)
        if args[0] == 'env':
            self.write(get_env())
        if args[0] == 'version':
            name = self.get_argument("name")
            self.write(get_current_version().get(name, ""))


def get_image_name(image_url, image_name, version):
    return image_url + "/" + image_name + ":" + version


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[(r'/(.*)', IndexHandler)],
        static_path=os.path.join(os.path.dirname(__file__), "k8s-deployment"),
        debug=False
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    print("listening on " + str(options.port))
    tornado.ioloop.IOLoop.instance().start()
