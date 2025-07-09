
import React from "react";
import { Button } from "@/components/ui/button";
import { Award } from "lucide-react";
import { HashLink } from 'react-router-hash-link';
import { Link } from "react-router-dom";

const NavBar = () => {
  return (
    <header className="w-full py-4 border-b border-gray-100">
      <div className="container mx-auto px-4 flex justify-between items-center">
        <Link to="/">  
          <div className="flex items-center space-x-2">
            <Award className="h-6 w-6 text-primary" />
            <span className="font-bold text-xl text-primary">StataGo Generator</span>
          </div>
        </Link> 
        <nav className="hidden md:flex items-center space-x-8">
        <HashLink smooth to="/#features"      className="text-sm font-medium text-gray-700 hover:text-primary transition-colors">
          Features
        </HashLink>
        <HashLink smooth to="/#how-it-works"  className="text-sm font-medium text-gray-700 hover:text-primary transition-colors">
          How It Works
        </HashLink>
        <HashLink smooth to="/#testimonials"  className="text-sm font-medium text-gray-700 hover:text-primary transition-colors">
          Testimonials
        </HashLink>
          <Link to="/upload" className="text-sm font-medium text-gray-700 hover:text-primary transition-colors">Upload Data</Link>
        </nav>
        
        <div className="flex space-x-4">
          <Button variant="outline" className="hidden md:block">Log In</Button>
          <Button asChild className="hidden md:block"><Link to="/upload">Get Started</Link></Button>
        </div>
      </div>
    </header>
  );
};

export default NavBar;
