import React from 'react';
import Router from './components/pages/Main/Router';
import { Switch, Route } from 'react-router-dom';
import { MAIN, ANALYSIS, OVERLAY, TACT } from './lib/api/Define/URL';

const App = () => {
  return (
    <>
      <Switch>
        <Route path={[MAIN, ANALYSIS, OVERLAY, TACT]}>
          <Router />
        </Route>
      </Switch>
    </>
  );
};

export default App;
