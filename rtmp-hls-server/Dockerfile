# Use alqutami/rtmp-hls as the base image
FROM alqutami/rtmp-hls

# Install necessary dependencies for Lua and OpenResty
RUN apt-get update && apt-get install -y \
    software-properties-common \
    wget \
    && add-apt-repository -y ppa:openresty/ppa \
    && apt-get update \
    && apt-get install -y openresty \
    && apt-get install -y luarocks

# Ensure OpenResty is using LuaJIT for Lua support in NGINX
RUN luarocks install lua-resty-core
RUN luarocks install lua-resty-lrucache

# Copy your custom NGINX configuration with Lua scripting
COPY custom.conf /etc/nginx/nginx.conf

# Define entrypoint to start OpenResty
CMD ["/usr/local/openresty/bin/openresty", "-g", "daemon off;"]
