# Start from the official OpenResty base image
FROM openresty/openresty:alpine

# Install FFmpeg for video processing
RUN apk add --no-cache ffmpeg

# Copy your custom NGINX configuration to the container
COPY conf/nginx_custom.conf /usr/local/openresty/nginx/conf/nginx.conf

# Expose the necessary ports
EXPOSE 1935 8080

# Start OpenResty (NGINX)
CMD ["/usr/local/openresty/bin/openresty", "-g", "daemon off;"]
