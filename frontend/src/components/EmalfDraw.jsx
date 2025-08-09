import React, { useState, useEffect } from 'react';
import { RefreshCw, Plus, Palette } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { toast } from '../hooks/use-toast';
import { Toaster } from './ui/toaster';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EmalfDraw = () => {
  const [currentIdea, setCurrentIdea] = useState('');
  const [allIdeas, setAllIdeas] = useState([]);
  const [newIdea, setNewIdea] = useState('');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Load ideas from backend API
  useEffect(() => {
    loadIdeas();
  }, []);

  const loadIdeas = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get(`${API}/ideas`);
      setAllIdeas(response.data);
      
      // Set initial random idea
      if (response.data.length > 0) {
        const randomIndex = Math.floor(Math.random() * response.data.length);
        setCurrentIdea(response.data[randomIndex].text);
      }
    } catch (error) {
      console.error('Error loading ideas:', error);
      toast({
        title: "Error",
        description: "Failed to load drawing ideas. Please refresh the page.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Get random idea with smooth animation from backend
  const getRandomIdea = async () => {
    if (isAnimating || isLoading) return;
    
    setIsAnimating(true);
    
    try {
      const response = await axios.get(`${API}/ideas/random`);
      
      setTimeout(() => {
        setCurrentIdea(response.data.text);
        setIsAnimating(false);
      }, 300);
    } catch (error) {
      console.error('Error getting random idea:', error);
      setIsAnimating(false);
      toast({
        title: "Error", 
        description: "Failed to get new challenge. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Add new idea to backend
  const addNewIdea = async () => {
    if (!newIdea.trim()) {
      toast({
        title: "Error",
        description: "Please enter a drawing idea",
        variant: "destructive",
      });
      return;
    }

    try {
      const response = await axios.post(`${API}/ideas`, {
        text: newIdea.trim()
      });

      // Update local state with new idea
      setAllIdeas(prev => [response.data, ...prev]);
      
      toast({
        title: "Success!",
        description: "Your drawing idea has been added and shared with everyone!",
      });
      
      setNewIdea('');
      setIsDialogOpen(false);
    } catch (error) {
      console.error('Error adding idea:', error);
      
      if (error.response?.status === 409) {
        toast({
          title: "Already exists",
          description: "This drawing idea already exists!",
          variant: "destructive",
        });
      } else {
        toast({
          title: "Error",
          description: "Failed to add your idea. Please try again.",
          variant: "destructive",
        });
      }
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-yellow-400 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-yellow-400 text-xl">Loading creative challenges...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      <Toaster />
      
      {/* Animated background particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
        <div className="absolute top-40 right-20 w-1 h-1 bg-yellow-300 rounded-full animate-ping delay-1000"></div>
        <div className="absolute bottom-32 left-1/4 w-1.5 h-1.5 bg-yellow-400 rounded-full animate-pulse delay-2000"></div>
        <div className="absolute bottom-20 right-1/3 w-1 h-1 bg-yellow-300 rounded-full animate-ping delay-500"></div>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <header className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Palette className="w-8 h-8 text-yellow-400" />
            <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-yellow-400 to-yellow-200 bg-clip-text text-transparent">
              EmalfDraw
            </h1>
          </div>
          <p className="text-xl md:text-2xl text-gray-300 font-light">
            Drawing Challenge of the Day
          </p>
        </header>

        {/* Main Content */}
        <div className="text-center mb-12">
          {/* Challenge Display */}
          <div className="mb-8">
            <h2 className="text-2xl md:text-3xl text-gray-400 mb-6 font-light">
              Today's Challenge
            </h2>
            
            <div className={`relative transition-all duration-300 transform ${
              isAnimating ? 'scale-95 opacity-50 rotate-1' : 'scale-100 opacity-100 rotate-0'
            }`}>
              <div className="bg-gradient-to-br from-gray-900 to-black border border-yellow-400/20 rounded-2xl p-8 md:p-12 shadow-2xl backdrop-blur-sm">
                <div className="absolute inset-0 bg-gradient-to-br from-yellow-400/5 to-transparent rounded-2xl"></div>
                <p className="text-2xl md:text-4xl font-bold text-white leading-relaxed relative z-10">
                  {currentIdea || "Loading your creative challenge..."}
                </p>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button
              onClick={getRandomIdea}
              disabled={isAnimating || isLoading}
              className="bg-yellow-400 hover:bg-yellow-500 text-black font-semibold px-8 py-6 text-lg rounded-xl transition-all duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-yellow-400/25 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RefreshCw className={`w-5 h-5 mr-2 transition-transform duration-300 ${
                isAnimating ? 'animate-spin' : ''
              }`} />
              New Challenge
            </Button>

            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button
                  variant="outline"
                  className="border-yellow-400 text-yellow-400 hover:bg-yellow-400 hover:text-black font-semibold px-8 py-6 text-lg rounded-xl transition-all duration-300 transform hover:scale-105"
                >
                  <Plus className="w-5 h-5 mr-2" />
                  Add Idea
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-gray-900 border-yellow-400/30 text-white">
                <DialogHeader>
                  <DialogTitle className="text-yellow-400 text-xl">Add Your Drawing Idea</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 pt-4">
                  <Input
                    placeholder="Enter your creative drawing challenge..."
                    value={newIdea}
                    onChange={(e) => setNewIdea(e.target.value)}
                    className="bg-black border-yellow-400/30 text-white placeholder-gray-500 focus:border-yellow-400"
                    onKeyPress={(e) => e.key === 'Enter' && addNewIdea()}
                  />
                  <div className="flex gap-3 justify-end">
                    <Button
                      variant="outline"
                      onClick={() => {
                        setIsDialogOpen(false);
                        setNewIdea('');
                      }}
                      className="border-gray-600 text-gray-400 hover:bg-gray-800"
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={addNewIdea}
                      className="bg-yellow-400 hover:bg-yellow-500 text-black font-semibold"
                    >
                      Add Idea
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {/* Stats */}
        <div className="text-center">
          <div className="inline-flex items-center gap-2 bg-gray-900/50 border border-yellow-400/20 rounded-full px-6 py-3 backdrop-blur-sm">
            <div className="w-3 h-3 bg-yellow-400 rounded-full animate-pulse"></div>
            <span className="text-gray-300">
              {allIdeas.length} creative challenges available
            </span>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-16 text-center">
          <p className="text-gray-500 text-sm">
            Get inspired. Draw something amazing. Share your creativity with everyone.
          </p>
        </footer>
      </div>
    </div>
  );
};

export default EmalfDraw;

