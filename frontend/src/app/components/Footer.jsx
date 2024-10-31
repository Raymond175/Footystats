import React from 'react'

function Footer() {
  return (
    <footer className="bg-green-900 text-white py-8">
        <div className="container mx-auto text-center">
          <p className="mb-4">&copy; 2024 FootStats. All rights reserved.</p>
          <div className="space-x-4">
            <a href="#" className="hover:underline">
              Privacy Policy
            </a>
            <a href="#" className="hover:underline">
              Terms of Service
            </a>
            <a href="#" className="hover:underline">
              Contact Us
            </a>
          </div>
        </div>
    </footer>
  )
}

export default Footer