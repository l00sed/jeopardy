var app = angular.module('jeopardy-creator',[]);
    app.controller('CreatorCtrl', function($scope, $http){
        $scope.main = {};
        $scope.searchTerm = '';
        $scope.searchResults = [];
        $scope.historicalQuestions = null;
        
        $scope.board = {
          "jeopardy": [
          ],
          "double-jeopardy": [
          ],
          "final-jeopardy": {
              "answer": "Who is some guy in Normandy But I just won $75,000!",
              "category": "MILITARY MEN",
              "question": "On June 6, 1944 he said, \"The eyes of the world are upon you\""
          }
        };
        
        // Load historical questions on initialization
        $http.get('../jeopardy_questions_archive_formatted.json').then(function(response) {
            $scope.historicalQuestions = response.data;
        }, function(error) {
            console.error('Error loading historical questions:', error);
        });

        $scope.load = function(){
            $scope.board = JSON.parse($scope.pre);
        };
        
        $scope.save = function(){
            // Prompt for filename
            var filename = prompt("Enter filename for the board (without .json extension):", "board_custom");
            
            if (!filename) {
                return; // User cancelled
            }
            
            // Remove .json extension if user added it
            filename = filename.replace(/\.json$/, '');
            
            // Send board data to server
            $http.post('/api/save-board', {
                filename: filename,
                board: $scope.board
            }).then(function(response) {
                if (response.data.success) {
                    alert('Board saved successfully to: ' + response.data.filepath);
                } else {
                    alert('Error saving board: ' + response.data.error);
                }
            }, function(error) {
                alert('Error saving board: ' + (error.data ? error.data.error : error.statusText));
            });
        };
        
        // Search categories by term
        $scope.searchCategories = function() {
            $scope.searchResults = [];
            
            if (!$scope.searchTerm || $scope.searchTerm.trim() === '') {
                return;
            }
            
            // Use semantic search API
            $http.get('/api/search-categories?q=' + encodeURIComponent($scope.searchTerm) + '&top_k=20')
                .then(function(response) {
                    if (response.data.success) {
                        $scope.searchResults = response.data.results;
                        console.log('Found ' + $scope.searchResults.length + ' categories');
                    }
                }, function(error) {
                    console.error('Semantic search error:', error);
                    // Fallback to basic keyword search if semantic search fails
                    $scope.basicKeywordSearch();
                });
        };
        
        // Fallback basic keyword search
        $scope.basicKeywordSearch = function() {
            $scope.searchResults = [];
            
            if (!$scope.searchTerm || $scope.searchTerm.trim() === '' || !$scope.historicalQuestions) {
                return;
            }
            
            var searchLower = $scope.searchTerm.toLowerCase();
            
            // Search through jeopardy round
            if ($scope.historicalQuestions.jeopardy) {
                $scope.historicalQuestions.jeopardy.forEach(function(category) {
                    if (category.name && category.name.toLowerCase().indexOf(searchLower) !== -1) {
                        $scope.searchResults.push({
                            name: category.name,
                            questions: category.questions,
                            round: 'jeopardy'
                        });
                    }
                });
            }
            
            // Search through double-jeopardy round
            if ($scope.historicalQuestions['double-jeopardy']) {
                $scope.historicalQuestions['double-jeopardy'].forEach(function(category) {
                    if (category.name && category.name.toLowerCase().indexOf(searchLower) !== -1) {
                        $scope.searchResults.push({
                            name: category.name,
                            questions: category.questions,
                            round: 'double-jeopardy'
                        });
                    }
                });
            }
        };
        
        // Import a category from search results to the specified round
        $scope.importCategory = function(category, targetRound) {
            if ($scope.board[targetRound].length >= 6) {
                alert('Cannot add more than 6 categories to ' + targetRound);
                return;
            }
            
            // Create a deep copy of the category
            var importedCategory = {
                name: category.name,
                questions: angular.copy(category.questions)
            };
            
            $scope.board[targetRound].push(importedCategory);
            
            // Optionally clear search after import
            // $scope.searchTerm = '';
            // $scope.searchResults = [];
        };
        
        $scope.addCategory = function(round){
            round.push({
                name:"AN ALBUM COVER",
                questions:[]
            });
        };
        $scope.addQuestion = function(category){
            category.questions.push({
                question:"THE BEATLES WHITE ALBUM IS THIS COLOR.",
                value:0,
                answer:"Who are the Beatles?"
            });
        };
        $scope.addImage = function(question) {
          question.image = "";
        };
        $scope.removeImage = function(question) {
          delete question.image;
        };
        $scope.addYouTube = function(question) {
          question.youtube = "";
        };
        $scope.removeYouTube = function(question) {
          delete question.youtube;
        };
    });