
import React from "react";
import { Button } from "@/components/ui/button";
import { GraduationCap } from "lucide-react";
import { Link } from "react-router-dom";

const CTASection = () => {
  return (
    <section className="py-20">
      <div className="container mx-auto px-4">
        <div className="bg-gradient-to-r from-primary to-blue-600 rounded-2xl p-10 md:p-16 text-white text-center fadeIn">
          <div className="flex justify-center mb-6">
            <div className="h-16 w-16 rounded-full bg-white/20 flex items-center justify-center">
              <GraduationCap className="h-8 w-8" />
            </div>
          </div>
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready to Excel in Your Econometrics Courses?</h2>
          <p className="text-xl opacity-90 max-w-2xl mx-auto mb-8">
            Join the students who are saving time and improving their grades with StataGo Generator.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Button size="lg" className="bg-white text-primary hover:bg-accent hover:text-accent-foreground px-8">
              <Link to="/upload">Get Started for Free</Link>
            </Button>

            <Button size="lg" className="bg-white text-primary hover:bg-accent hover:text-accent-foreground px-8">
              Login
            </Button>
            
            
          </div>
        </div>
      </div>
    </section>
  );
};

export default CTASection;
