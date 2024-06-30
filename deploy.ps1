# Container name
$containerName = "air-purifier-api"

# Function to check if a container is running
function Is-ContainerRunning {
    docker ps -q --filter "name=$containerName"
}

# Function to check if a container exists (running or stopped)
function Is-ContainerExists {
    docker ps -aq --filter "name=$containerName"
}

# Function to check if an image exists
function Is-ImageExists {
    docker images -q $containerName
}

# Stop and remove the container if it's running
if (Is-ContainerRunning) {
    Write-Output "Stopping the running container..."
    docker stop $containerName
}

# Remove the container if it exists
if (Is-ContainerExists) {
    Write-Output "Removing the container..."
    docker rm $containerName
}

# Remove the Docker image if it exists
if (Is-ImageExists) {
    Write-Output "Removing the Docker image..."
    docker rmi $containerName
}

# Build the new Docker image
Write-Output "Building the new Docker image..."
docker build -t $containerName .

# Run the new container
Write-Output "Running the new container..."
docker run -d -p 8000:8000 --name $containerName $containerName

Write-Output "Deployment completed successfully."
