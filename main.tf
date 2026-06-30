provider "aws" {
  region = "us-west-1"
}


resource "aws_ecr_repository" "tf-automated-docker-image-deployment" {
  name                 = "automated-docker-image-deployment"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}