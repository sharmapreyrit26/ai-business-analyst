import { useState } from 'react'
import { Route, Routes } from 'react-router-dom'
import { Header } from './components/Header'
import { Sidebar } from './components/Sidebar'
import Analyst from './pages/Analyst'
import Customers from './pages/Customers'
import Logistics from './pages/Logistics'
import Overview from './pages/Overview'
import Products from './pages/Products'
import Scenario from './pages/Scenario'

export default function App(){
 const [month,setMonth]=useState('2018-06')
 return <div className="app-shell"><Sidebar/><main className="main"><Header month={month} onMonthChange={setMonth}/><div className="content"><Routes><Route path="/" element={<Overview month={month}/>}/><Route path="/products" element={<Products month={month}/>}/><Route path="/customers" element={<Customers/>}/><Route path="/logistics" element={<Logistics month={month}/>}/><Route path="/analyst" element={<Analyst month={month}/>}/><Route path="/scenario" element={<Scenario month={month}/>}/></Routes></div></main></div>
}
