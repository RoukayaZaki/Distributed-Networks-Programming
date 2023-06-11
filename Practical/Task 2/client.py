import grpc
import calculator_pb2 as service
import calculator_pb2_grpc as stub

def Add(a, b):
    args = service.Request(a= a, b= b)
    response = stub.Add(args)
    print(f"Add({a}, {b}) = {response}")

def Subtract(a, b):
    args = service.Request(a= a, b= b)
    response = stub.Subtract(args)
    print(f"Subtract({a}, {b}) = {response}")

def Multiply(a, b):
    args = service.Request(a= a, b= b)
    response = stub.Multiply(args)
    print(f"Multiply({a}, {b}) = {response}")

def Divide(a, b):
    args = service.Request(a= a, b= b)
    response = stub.Divide(args)
    print(f"Divide({a}, {b}) = {response}")

if __name__ == '__main__':
    with grpc.insecure_channel('localhost:50000') as channel:
        stub = stub.CalculatorStub(channel)
        Add(10, 2)
        Subtract(10,2)
        Multiply(10,2)
        Divide(10,2)
        Divide(10,0)
