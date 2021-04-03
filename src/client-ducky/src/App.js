import React, {useEffect, useState} from "react"
import { BrowserRouter as Router, Switch, Route, Redirect } from "react-router-dom"
import Home from "./components/Home"
import AboutUs from "./components/AboutUs"
import Header from "./components/Header"
import Footer from "./components/Footer"
import Login from "./components/Login"
import Profile from "./components/Profile"
import Search from "./components/Search"
import SignUp from "./components/SignUp";
import Details from "./components/Detail";
import Reservation from "./components/Reservation";
import "../node_modules/bootstrap/dist/css/bootstrap.min.css";
import "./css/styles.css"

function App() {

  const [token, setToken] = useState(localStorage.getItem('token'));
  const [isAuthenticated, setIsAuthenticated] = useState(localStorage.getItem('isAuthenticated'));

  useEffect(() => {
    if(token == null && localStorage.getItem('token')) {
      setToken(token)
      setIsAuthenticated(true)
    }
  }, [])


  return (
      <Router>
        <Header isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated}/>
        {token ? (
        <div>
          <Switch>
            <Route exact path="/home">
              <Home/>
            </Route>
            <Route exact path="/login">
              <Login setToken={setToken} setIsAuthenticated={setIsAuthenticated}/>
            </Route>
            <Route path="/about-us">
            <AboutUs/>
          </Route>
          <Route path="/profile">
            <Profile/>
          </Route>
          <Route path="/s">
            <Search/>
          </Route>
           <Route path="/signup">
            <SignUp/>
          </Route>
            <Route path="/details">
            <Details/>
          </Route>
          <Route path="/reservation">
            <Reservation/>
          </Route>
          </Switch>
          <Footer/>
        </div>
        ): 
        <Switch>
          <Login path='/login' setToken={setToken} setIsAuthenticated={setIsAuthenticated}/>
          <SignUp path='/signup' setToken={setToken} setIsAuthenticated={setIsAuthenticated}/>
        </Switch>
        }
      </Router>
  );
}

export default App;
