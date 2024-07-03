from flask import Flask, request, jsonify
from cpu import CPU

app = Flask(__name__)
cpu = CPU()

@app.route('/api/run', methods=['POST'])
def run():
    data = request.json
    program = data.get('program')
    start_address = data.get('start_address', 0)
    
    # Load program into CPU memory
    cpu.load_memory_dump(program)
    cpu.pc = start_address
    
    # Run the CPU emulator
    cpu.run()
    
    return jsonify({"message": "Program executed successfully", "registers": cpu.registers})

if __name__ == '__main__':
    app.run(debug=True)
