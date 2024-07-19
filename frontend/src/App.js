import React from 'react';
import { Route, Switch } from 'react-router-dom';
import Editor from './components/Editor';
import CPUDashboard from './components/CPUDashboard';
import Login from './components/Login';
import Signup from './components/Signup';

function App() {
  return (
    <div className="App">
      <Switch>
        <Route path="/editor" component={Editor} />
        <Route path="/cpu" component={CPUDashboard} />
        <Route path="/login" component={Login} />
        <Route path="/signup" component={Signup} />
      </Switch>
    </div>
  );
}

export default App;