import math
import grpc
import calculator_pb2
import calculator_pb2_grpc
from concurrent.futures import ThreadPoolExecutor

class CalculatorServicer(calculator_pb2_grpc.CalculatorServicer):

    def Add(self, request, context):
        result = request.a + request.b
        print(f"Add({request.a}, {request.b})")
        return calculator_pb2.Response(result=result)

    def Subtract(self, request, context):
        result = request.a - request.b
        print(f"Subtract({request.a}, {request.b})")
        return calculator_pb2.Response(result=result)

    def Multiply(self, request, context):
        result = request.a * request.b
        print(f"Multiply({request.a}, {request.b})")
        return calculator_pb2.Response(result=result)

    def Divide(self, request, context):
        print(f"Divide({request.a}, {request.b})")
        if request.b == 0:
            result = math.nan
        else:
            result = request.a / request.b
        return calculator_pb2.Response(result=result)

    
if __name__ == '__main__':
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    calculator_pb2_grpc.add_CalculatorServicer_to_server(CalculatorServicer(), server)
    server.add_insecure_port('0.0.0.0:50000')
    server.start()
    print('gRPC server is listening on 0.0.0.0:50000')
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)
        print("Shutting down...")
