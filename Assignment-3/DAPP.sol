pragma solidity ^0.8.0;

contract DAppFactChecker {
    
    // Struct for Article
    struct Article {
        uint ID;                        // Unique ID for each article
        string news;                    //content of news
        uint topic;                     // int representing the topic
        bool truth;                     // boolean representing the truth of the article
        mapping(address => bool) votes; // Mapping to store votes by address
        
    }

    // Struct for Person or voters
    struct Person {
        uint ID;                        // Unique ID for each person
        uint truthprob;                      // Truth probability represented as an integer between 0 to 100
        mapping(uint => uint) trustworthy;  // Mapping from topic to trustworthiness
        bool isfactchecker; // Mapping to check if person is a fact checker for a topic
        uint amount;                        // Amount of tokens representing reputation
        mapping(uint => bool) voted;        // Mapping to check if person has voted on an article
    }

    Article[] public articles;              // Array to store articles
    Person[] public persons;               // Array to store persons
    mapping(address => bool) public registeredFactCheckers; // Mapping to check if an address is a registered fact checker

     // Constructor to initialize persons with different trust levels
      // Constructor code is only run when the contract is created and cannot be called again
    constructor(uint n, uint8 p, uint8 q) {
        require(p <= 100 && q <= 100, "p and q should be percentages");
        
        uint numVeryTrustworthy = p * (100 - q) * n / 10000;
        uint numMalicious = q * n / 100;
        uint numNormal = n - numVeryTrustworthy - numMalicious;
        
        for (uint i = 0; i < numVeryTrustworthy; i++) {
            persons.push(Person(i, 90, 100)); // adding more trustworthy persons
        }
        
        for (uint i = numVeryTrustworthy; i < numVeryTrustworthy + numNormal; i++) {
            persons.push(Person(i, 70, 100)); //adding honest but less trustworthy persons
        }
        
        for (uint i = numVeryTrustworthy + numNormal; i < n; i++) {
            persons.push(Person(i, 0, 100)); // adding malicious persons
        }
}
    // Function to register as a fact checker
    // External functions can be called from other contracts or transactions
    // anyone person can  call this function
    function registerAsFactChecker() external {
        persons[msg.sender].isfactchecker = true;
    }

    //Only authorized users can add articles, typically the application owner or designated administrators.
    // This function is used to add new articles to the system.
    // internal functions can only be called from within the contract
    function addArticle(string memory _news, uint _topic, bool _truth) internal {
        articles.push(Article(articles.length, _news, _topic, _truth));
    }

    // Any person can vote on an article.
    // The limitation is that a person can only vote once for each article.
    // The function returns the vote of the person.
    // external functions can be called from other contracts or transactions
    function vote(Article memory article) external returns (bool) {
        if (persons[msg.sender].voted[article.ID]) {
            // If the person has already voted for this article, return the same vote
            return persons[msg.sender].voted[article.ID];
        } else {
            // New article to vote
            // Determine the vote based on the person's truth probability
            bool vote = persons[msg.sender].truthprob >= uint(keccak256(abi.encodePacked(block.timestamp, msg.sender, article.ID))) % 100;

            // Store the vote of this person in the article's votes mapping
            articles[article.ID].votes[msg.sender] = vote;
            // Store the vote in the person's voted mapping
            persons[msg.sender].voted[article.ID] = vote;

            return vote;
        }
    }



    // This function is internal and used within the contract.
    // It calculates the committee's vote based on the weighted trustworthiness of its members.
    function selectCommittee(uint topic, uint committeeSize) internal view returns (Person[] memory) {
        Person[] memory activePersons;              // Array to store active persons
        uint totalReputation;                       // Total reputation of all active persons

        // Selecting active persons who are fact checkers for the given topic
        for (uint i = 0; i < persons.length; i++) {
            if (persons[i].isfactchecker[topic]) {
                totalReputation += persons[i].trustworthy[topic];
                activePersons.push(persons[i]);
            }
        }    
        Person[] memory committee = new Person[](committeeSize);
        

        // Selecting committee members based on their trustworthiness
        for (uint i = 0; i < committeeSize; i++) {
            uint rand = uint(keccak256(abi.encodePacked(block.timestamp, msg.sender, i))) % totalReputation;
            // generating a random number between 0 and totalReputation
            //This ensures that each selection of a committee member has a unique random number seed, 
            // preventing the same committee member from being selected multiple times.
            uint cumulativeProbability;
            for (uint j = 0; j < activePersons.length; j++) {
                cumulativeProbability += activePersons[j].trustworthy[topic];
                if (rand < cumulativeProbability) { // Selecting a person based on their trustworthiness 
                    committee[i] = activePersons[j];
                    break;
                }
            }
        }
        return committee;
    }

    // Any person can request a fact check for an article.
    // The function returns the final result of the fact check.
    // external functions can be called from other contracts or transactions
    function requestFactCheck(uint articleID) external returns (bool) {
        Article storage article = articles[articleID];
    
        uint topic = article.topic;
        uint committeeSize = persons.length / 2;  // Selecting half of the persons as committee members
        Person[] memory committee = selectCommittee(topic, committeeSize); // Selecting committee members
        bool result = committeeVote(article, committee);  //final result of the fact check by committee
        updateTrustworthiness(article, persons, result); // Updating trustworthiness of all voters and committee members and amount
        article.valid = result;  // Storing the result in the article
        return result;
    }

    // This function is internal and used within the contract.
    // gives the final result of the fact check by the committee by taking the weighted truth average of all persons in the committee.
    // returns the result of the fact check.
    function committeeVote(Article memory article, Person[] memory committee) internal view returns (bool) {
        uint votesTrue;
        uint votesFalse;

        //  taking weighted truth avg of all persons in committee
        for (uint i = 0; i < committee.length; i++) {
            if (article.votes[committee[i]] == true) {
                votesTrue += committee[i].trustworthy[article.topic];
            } else {
                votesFalse += committee[i].trustworthy[article.topic];
            }
        }
        // returning the result based on the weighted average
        return votesTrue > votesFalse;
    }

    // This function is internal and used within the contract.
    // It updates the trustworthiness of all voters and committee members based on the result of the fact check.
    // here we are assuming everyone has voted and updating everyone's trustworthiness
    function updateTrustworthiness(Article memory article, Person[] memory persons, bool result) internal {
        for (uint i = 0; i < committee.length; i++) {
            Person storage person = persons[committee[i].ID];
            // Updating trustworthiness based on the result from committee vote
            if (article.votes[person] == result) {
                // If the person voted correctly, increase their trustworthiness and give them more tokens or amount
                person.amount += 1;
                person.trustworthy[article.topic] += 1;
                if (person.trustworthy[article.topic] > 100) {
                    person.trustworthy[article.topic] = 100;
                }
            } else {
                // If the person voted incorrectly, decrease their trustworthiness and take away some tokens or amount
                person.amount -= 1;
                person.trustworthy[article.topic] -= 1;
                if (person.trustworthy[article.topic] < 0) {
                    person.trustworthy[article.topic] = 0;
                }
            }
        }
    }




}

