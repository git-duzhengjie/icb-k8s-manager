#!/bin/bash

while getopts "v:e:o:" opt;do
  case $opt in 
    v)
      update_version $OPTARG
      ;;
    o)
      old=$OPTARG
      ;;
    e)
      new=$OPTARG
      ;;
    \?)
      echo "invalid option: -$OPTARG"
      ;;
   esac
done

update_version(){      
  kubectl set image deploy gateway-app gateway-app=10.10.10.3:5000/web/gateway-app:$1 -n icb
  kubectl set image deploy gateway-management gateway-management=10.10.10.3:5000/web/gateway-management:$1 -n icb
  kubectl set image deploy micro-main micro-main=10.10.10.3:5000/web/micro-main:$1 -n icb
  kubectl set image deploy micro-user micro-user=10.10.10.3:5000/web/micro-user:$1 -n icb
  kubectl set image deploy micro-story micro-story=10.10.10.3:5000/web/micro-story:$1 -n icb
  kubectl set image deploy micro-market micro-market=10.10.10.3:5000/web/micro-market:$1 -n icb
  kubectl set image deploy micro-sword micro-sword=10.10.10.3:5000/web/micro-sword:$1 -n icb
}

if [[ "$old" != "" && "$new" != "" ]];then
  sed -i s/$old/$new/g yaml/icb-deployment/*
  kubectl apply -f yaml/icb-deployment/
fi
