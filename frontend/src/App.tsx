import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Directories from './pages/Directories'
import DirectoryForm from './pages/DirectoryForm'
import ProductForm from './pages/ProductForm'
import Products from './pages/Products'
import SubmissionDetail from './pages/SubmissionDetail'
import Submissions from './pages/Submissions'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/products" element={<Products />} />
        <Route path="/products/new" element={<ProductForm />} />
        <Route path="/products/:id/edit" element={<ProductForm />} />
        <Route path="/directories" element={<Directories />} />
        <Route path="/directories/new" element={<DirectoryForm />} />
        <Route path="/directories/:id/edit" element={<DirectoryForm />} />
        <Route path="/submissions" element={<Submissions />} />
        <Route path="/submissions/:id" element={<SubmissionDetail />} />
      </Routes>
    </Layout>
  )
}

export default App
