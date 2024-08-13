FROM node:18

WORKDIR /app
COPY package*.json ./
COPY githook.cjs ./
# Install dependencies
RUN npm install
# Install Google Chrome
RUN apt-get update && apt-get install -y wget gnupg
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get update && apt-get install -y google-chrome-stable

# Set the CHROME_BIN environment variable
ENV CHROME_BIN=/usr/bin/google-chrome

# Ensure the chrome binary is linked correctly
RUN ln -sf /usr/bin/google-chrome /usr/local/bin/google-chrome
# Copy the rest of the application code to the working directory
COPY . .
ENV CHROME_BIN=/usr/bin/google-chrome

# Build the application
RUN npm run build

# Expose the port the app runs on
EXPOSE 3000

# Define the command to run the application
CMD ["npm", "start"]

