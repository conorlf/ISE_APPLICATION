
import React from "react";
import NavBar from "@/components/NavBar";
import HeroSection from "@/components/HeroSection";
import FeaturesSection from "@/components/FeaturesSection";
import HowItWorksSection from "@/components/HowItWorksSection";
import TestimonialsSection from "@/components/TestimonialsSection";
import CTASection from "@/components/CTASection";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <NavBar />
      <main className="flex-grow">
        <section id="heroSection">
          <HeroSection />
        </section>
       
         <section id="features">
          <FeaturesSection />
        </section>

        <section id="howItWorks">
          <HowItWorksSection />
        </section>

        <section id="testimonials">
          <TestimonialsSection />
        </section>
        <section id="ctaSection"><CTASection/></section>
        
      </main>
      <Footer />
    </div>
  );
};

export default Index;
