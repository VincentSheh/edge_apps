# Use the official Node.js image from Docker Hub
FROM node:14

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install npm dependencies
RUN npm install

# Copy the entire project to the working directory
COPY . .

# Expose the port that the app runs on
EXPOSE 8080

# Define the command to start the application
CMD ["npm", "start"]
