#!/bin/bash

name=backend
user=user # you can use "$USER", if your user can access docker without sudo
static=static_back
media=media_back
media_local="$(pwd)"/$media
static_local="$(pwd)"/$static

rm -rf $static_local
mkdir -p $static_local
rm -rf $media_local
mkdir -p $media_local

docker build -t $name .

docker stop $name || true
docker rm $name || true

docker volume rm $static || true
docker volume create --driver local \
	--opt type=none \
	--opt device=$static_local \
	--opt o=bind $static

docker volume rm $media || true
docker volume create --driver local \
	--opt type=none \
	--opt device=$media_local \
	--opt o=bind $media

docker run -d --name $name --network 'host' \
	-v $static:/usr/src/app/$static \
	-v $media:/usr/src/app/$media \
	--restart=unless-stopped \
	$name

chown -R $user: $static_local
chown -R $user: $media_local
