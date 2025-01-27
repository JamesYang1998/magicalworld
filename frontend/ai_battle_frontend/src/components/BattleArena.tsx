import { useState, useEffect } from 'react';
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Label } from "./ui/label";
import { Sword, Trophy, Loader2 } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "./ui/alert";
interface Character {
  name: string;
  side: 'left' | 'right';
  image: string;
}

interface Message {
  role: string;
  content: string;
}

interface Battle {
  id: string;
  messages: Message[];
  status: string;
  winner?: string;
  scores?: {
    openai: number;
    deepseek: number;
  };
}

const characters: Record<string, Character> = {
  openai: {
    name: 'OpenAI',
    side: 'right',
    image: '/assets/characters/openai/openai_normal.png',
  },
  deepseek: {
    name: 'DeepSeek',
    side: 'left',
    image: '/assets/characters/deepseek/deepseek_normal.png',
  },
};

export function BattleArena() {
  const [topic, setTopic] = useState("");
  const [battle, setBattle] = useState<Battle | null>(() => {
    const saved = localStorage.getItem('currentBattle');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [twitterUsername, setTwitterUsername] = useState(() => {
    return localStorage.getItem('twitterUsername') || "";
  });
  const [voteError, setVoteError] = useState<string | null>(null);
  const [votes, setVotes] = useState<any>(() => {
    const saved = localStorage.getItem('currentVotes');
    return saved ? JSON.parse(saved) : null;
  });

  // Load battle state and votes on mount
  useEffect(() => {
    const savedBattle = localStorage.getItem('currentBattle');
    if (savedBattle) {
      const parsedBattle = JSON.parse(savedBattle);
      setBattle(parsedBattle);
      if (parsedBattle.status === 'completed') {
        fetchVotes(parsedBattle.id);
      }
    }
  }, []);

  // Save battle state when it changes
  useEffect(() => {
    if (battle) {
      localStorage.setItem('currentBattle', JSON.stringify(battle));
    }
  }, [battle]);

  const messages = battle?.messages.slice(1) || [];

  const createBattle = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/battles`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic, rounds: 3 }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to create battle');
      }
      
      const data = await response.json();
      setBattle(data);
      await processRound(data.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const processRound = async (battleId: string) => {
    try {
      setLoading(true);
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/battles/${battleId}/round`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('Failed to process round');
      }
      
      const data = await response.json();
      setBattle(data);
      
      if (data.status === 'completed') {
        await fetchVotes(battleId);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const fetchVotes = async (battleId: string) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/battles/${battleId}/votes`);
      if (!response.ok) {
        throw new Error('Failed to fetch votes');
      }
      const data = await response.json();
      setVotes(data);
      localStorage.setItem('currentVotes', JSON.stringify(data));
    } catch (err) {
      setVoteError(err instanceof Error ? err.message : 'Failed to fetch votes');
    }
  };

  const handleVote = async (chosenAi: string) => {
    if (!battle || !twitterUsername) return;
    
    try {
      setLoading(true);
      setVoteError(null);
      
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/battles/${battle.id}/vote`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          twitter_username: twitterUsername.replace('@', ''),
          chosen_ai: chosenAi,
        }),
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to submit vote');
      }
      
      const data = await response.json();
      setVotes(data);
      localStorage.setItem('currentVotes', JSON.stringify(data));
      
      const battleResponse = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/battles/${battle.id}`);
      if (battleResponse.ok) {
        const battleData = await battleResponse.json();
        setBattle(battleData);
      }
    } catch (err) {
      setVoteError(err instanceof Error ? err.message : 'Failed to submit vote');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="container mx-auto px-4 py-2 md:py-4 space-y-4 max-w-7xl">
        <Card className="w-full">
          <CardHeader className="space-y-2 md:space-y-3">
            <CardTitle className="flex items-center gap-2 text-xl md:text-2xl">
              <Sword className="w-5 h-5 md:w-6 md:h-6" />
              AI Battle Arena
            </CardTitle>
            <CardDescription className="text-sm md:text-base">
              Watch OpenAI and DeepSeek battle it out in a verbal showdown!
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="topic" className="text-sm md:text-base">Battle Topic</Label>
                <Input
                  id="topic"
                  placeholder="Enter a topic for the AI battle..."
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  disabled={loading || !!battle}
                  className="w-full"
                />
              </div>

              {!battle && (
                <Button 
                  onClick={createBattle} 
                  disabled={!topic || loading}
                  className="w-full"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating Battle...
                    </>
                  ) : (
                    'Start Battle'
                  )}
                </Button>
              )}

              {battle && (
                <div className="space-y-4">
                  <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
                      {/* DeepSeek Column */}
                      <div className="flex flex-col items-center space-y-4">
                        <div className="relative w-32 sm:w-40 md:w-48 lg:w-56 xl:w-64 aspect-square transition-transform hover:scale-105">
                          <img
                            src={characters.deepseek.image}
                            alt="DeepSeek"
                            className="w-full h-full object-cover rounded-lg shadow-lg transition-all duration-300 hover:shadow-xl"
                            loading="lazy"
                          />
                        </div>
                        <div className="w-full space-y-4 px-2 sm:px-4">
                          {messages
                            .filter((_, index) => index % 2 === 1)
                            .map((message, index) => (
                              <div
                                key={index}
                                className="flex items-start space-x-2"
                              >
                                <div className="flex-1">
                                  <Card className="bg-purple-50 hover:bg-purple-100 transition-colors">
                                    <CardContent className="p-3 sm:p-4 lg:p-6">
                                      <p className="font-semibold text-purple-700 text-sm sm:text-base">DeepSeek</p>
                                      <p className="mt-2 text-gray-700 text-sm sm:text-base leading-relaxed">{message.content}</p>
                                    </CardContent>
                                  </Card>
                                </div>
                              </div>
                            ))}
                        </div>
                      </div>

                      {/* OpenAI Column */}
                      <div className="flex flex-col items-center space-y-4">
                        <div className="relative w-32 sm:w-40 md:w-48 lg:w-56 xl:w-64 aspect-square transition-transform hover:scale-105">
                          <img
                            src={characters.openai.image}
                            alt="OpenAI"
                            className="w-full h-full object-cover rounded-lg shadow-lg transition-all duration-300 hover:shadow-xl"
                            loading="lazy"
                          />
                        </div>
                        <div className="w-full space-y-4 px-2 sm:px-4">
                          {messages
                            .filter((_, index) => index % 2 === 0)
                            .map((message, index) => (
                              <div
                                key={index}
                                className="flex items-start space-x-2"
                              >
                                <div className="flex-1">
                                  <Card className="bg-blue-50 hover:bg-blue-100 transition-colors">
                                    <CardContent className="p-3 sm:p-4 lg:p-6">
                                      <p className="font-semibold text-blue-700 text-sm sm:text-base">OpenAI</p>
                                      <p className="mt-2 text-gray-700 text-sm sm:text-base leading-relaxed">{message.content}</p>
                                    </CardContent>
                                  </Card>
                                </div>
                              </div>
                            ))}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Battle Controls */}
                  <div className="mt-6 lg:mt-8 w-full max-w-lg mx-auto px-4">
                    {battle.status === 'in_progress' && (
                      <Button
                        onClick={() => processRound(battle.id)}
                        disabled={loading}
                        className="w-full sm:w-auto sm:min-w-[240px] mx-auto block text-base"
                        size="lg"
                      >
                        {loading ? (
                          <>
                            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                            Processing Round...
                          </>
                        ) : (
                          'Next Round'
                        )}
                      </Button>
                    )}

                    {battle.status === 'completed' && (
                      <div className="space-y-4">
                        <Card className="bg-green-50">
                          <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                              <Trophy className="w-6 h-6 text-yellow-500" />
                              Battle Complete!
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <p className="text-lg font-semibold">
                              Winner: {battle.winner ? battle.winner.toUpperCase() : 'Pending Votes'}
                            </p>
                            {battle.scores && (
                              <div className="mt-2 grid grid-cols-2 gap-4">
                                <div className="text-center p-4 bg-blue-100 rounded-lg">
                                  <p className="font-semibold text-blue-700">OpenAI Score</p>
                                  <p className="text-2xl">{battle.scores.openai}</p>
                                </div>
                                <div className="text-center p-4 bg-purple-100 rounded-lg">
                                  <p className="font-semibold text-purple-700">DeepSeek Score</p>
                                  <p className="text-2xl">{battle.scores.deepseek}</p>
                                </div>
                              </div>
                            )}
                          </CardContent>
                        </Card>

                        <Card>
                          <CardHeader>
                            <CardTitle>Vote for Your Favorite AI</CardTitle>
                            <CardDescription>
                              Must be a follower of @jimsyoung_ on Twitter to vote
                            </CardDescription>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-4">
                              <div className="space-y-2">
                                <Label htmlFor="twitter-username">Twitter Username</Label>
                                <Input
                                  id="twitter-username"
                                  placeholder="@username"
                                  value={twitterUsername}
                                  onChange={(e) => setTwitterUsername(e.target.value)}
                                />
                              </div>
                              <div className="grid grid-cols-2 gap-4">
                                <Button
                                  onClick={() => handleVote('openai')}
                                  disabled={loading || !twitterUsername}
                                  className="w-full bg-blue-500 hover:bg-blue-600"
                                >
                                  Vote for OpenAI
                                </Button>
                                <Button
                                  onClick={() => handleVote('deepseek')}
                                  disabled={loading || !twitterUsername}
                                  className="w-full bg-purple-500 hover:bg-purple-600"
                                >
                                  Vote for DeepSeek
                                </Button>
                              </div>
                              {voteError && (
                                <Alert variant="destructive">
                                  <AlertTitle>Error</AlertTitle>
                                  <AlertDescription>{voteError}</AlertDescription>
                                </Alert>
                              )}
                              {votes && (
                                <div className="grid grid-cols-2 gap-4 mt-4">
                                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                                    <p className="font-semibold text-blue-700">OpenAI Votes</p>
                                    <p className="text-2xl">{votes.vote_counts.openai}</p>
                                  </div>
                                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                                    <p className="font-semibold text-purple-700">DeepSeek Votes</p>
                                    <p className="text-2xl">{votes.vote_counts.deepseek}</p>
                                  </div>
                                </div>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {error && (
          <Alert variant="destructive">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
      </div>
    </>
  );
}
