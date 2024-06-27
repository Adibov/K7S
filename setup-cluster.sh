helm upgrade -i \
  --repo https://kubernetes.github.io/ingress-nginx \
  nginx-ingress \
  --version 4.10.1 \
  ingress-nginx

public_ip=$(kubectl get svc \
  -l app.kubernetes.io/name=ingress-nginx | grep -i loadbalancer | awk '{print $3}')

line_to_add="$public_ip example.local"
if ! grep -Fxq "$line_to_add" /etc/hosts; then
    echo "$line_to_add" >> /etc/hosts
fi