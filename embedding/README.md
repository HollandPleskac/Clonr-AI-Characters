### Importing to server

This is still a WIP, not sure yet how to port this, other than making a poetry package and importing it.

To run the server, just launch `python -m app.server`. We provide an example client for accessing the remote procedure calls (RPCs), but this same client code is duplicated inside of backend where it is also called.

### Compiling

Make sure that you've installed grpcio. On a mac M1/M2, the installation instructions are kinda fucked, you have to install from source using pip install --all or something. Once that works, from the root directory, run
```
python -m grpc_tools.protoc --proto_path=./proto --python_out=./embedding/pb --pyi_out=./embedding/pb --grpc_python_out=./embedding/pb embedding.proto```
, which is also given as a shell script `compile_proto.sh`, to auto-generate the protobuf code.

Note that protobuf will add Servicer to the end of any service name, and auto create a function like add_<name>Servicer_to_server.

To run the server, you just run python -m embedding.server from the root of the repository


### Accessing locally

You can spin up the gRPC server via `docker compose up embedding`. If you are having trouble with the client, make sure that host=localhost when running locally, and host=embedding (or whatever is in the .env) when running inside of docker compose