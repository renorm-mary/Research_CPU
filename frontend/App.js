import React, { useState } from 'react';

function App() {
    const [program, setProgram] = useState('');
    const [result, setResult] = useState(null);

    const handleRun = async () => {
        const response = await fetch('/api/run', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ program })
        });
        const data = await response.json();
        setResult(data);
    };

    return (
        <div>
            <h1>CPU Emulator</h1>
            <textarea value={program} onChange={(e) => setProgram(e.target.value)} rows="10" cols="50"></textarea>
            <br />
            <button onClick={handleRun}>Run Program</button>
            {result && (
                <div>
                    <h2>Result</h2>
                    <pre>{JSON.stringify(result, null, 2)}</pre>
                </div>
            )}
        </div>
    );
}

export default App;