import React, { useState } from 'react';
import api from '../api';

const Editor = () => {
  const [code, setCode] = useState('');

  const saveCode = async () => {
    const token = localStorage.getItem('token');
    await api.post('/compile', { code }, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
  };

  return (
    <div>
      <textarea value={code} onChange={(e) => setCode(e.target.value)} />
      <button onClick={saveCode}>Save Code</button>
    </div>
  );
};

export default Editor;