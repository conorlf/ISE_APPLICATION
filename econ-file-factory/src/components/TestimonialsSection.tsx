
import React from "react";
import { Card, CardContent } from "@/components/ui/card";

interface TestimonialProps {
  quote: string;
  name: string;
  role: string;
  school: string;
}

const Testimonial = ({ quote, name, role, school }: TestimonialProps) => {
  return (
    <Card className="h-full">
      <CardContent className="p-6">
        <div className="mb-4">
          {[...Array(5)].map((_, i) => (
            <span key={i} className="text-yellow-400 mr-1">★</span>
          ))}
        </div>
        <p className="text-gray-700 mb-6 italic">"{quote}"</p>
        <div>
          <p className="font-semibold">{name}</p>
          <p className="text-sm text-gray-500">{role}, {school}</p>
        </div>
      </CardContent>
    </Card>
  );
};

const TestimonialsSection = () => {
  const testimonials = [
    {
      quote: "StataGo Generator saved me hours of work on my econometrics project. The generated data sets were perfect for my analysis.",
      name: "John",
      role: "BESS Student",
      school: "Trinity College Dublin"
    },
    {
      quote: "I was struggling with my plotting regressions assignment until I found this tool. The reports it generated helped me understand the concepts better.",
      name: "Sarah",
      role: "Economic and Finance Student",
      school: "University College Dublin"
    },
    {
      quote: "As a TA for an intro econometrics course, I recommend this to all my students. It's like having a personal econometrics tutor.",
      name: "Michael ",
      role: "Teaching Assistant",
      school: "DCU"
    }
  ];

  return (
    <section id="testimonials" className="py-20 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16 fadeIn">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">What Students Say</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Econometrics students are achieving better grades with our file generation tools.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 fadeIn">
          {testimonials.map((testimonial, index) => (
            <Testimonial 
              key={index}
              quote={testimonial.quote}
              name={testimonial.name}
              role={testimonial.role}
              school={testimonial.school}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default TestimonialsSection;
