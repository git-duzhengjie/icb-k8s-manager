# 概览
> 为用户提供动态发布服务到k8s集群和查看k8s集群服务版本接口

# API
- __更新__：/update?service_name=&version=&image_name= 
 >service_name表示服务名，image_name表示镜像名，version表示版本号
 
- __查看__：/version?name= 
>查看当前k8s集群中运行的服务版本号，name表示服务名
