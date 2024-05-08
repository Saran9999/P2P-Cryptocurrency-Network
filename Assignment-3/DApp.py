import argparse
import random
import matplotlib.pyplot as plt

class Article:
    """class for article data
    """
    def __init__(self,ID : int,news : str, topic : int, truth = True):
        """Initilize articles of news

        Args:
            ID (int): Article ID
            news (str): Article news string
            topic (int): Topic number
            truth (bool, optional): Article is truth or fake. Defaults to True.
        """
        self.ID = ID
        self.news = news
        self.topic = topic
        self.truth = truth

    def validity(self,val : bool):
        """To change the validity of news after voting

        Args:
            val (bool): Truth value based on voting
        """
        self.truth = val
    
class Person:
    """class for each person data and functioning
    """
    def __init__(self,ID : int,tprob : float):
        """Initilizing the person data

        Args:
            ID (int): ID of person
            tprob (float): Truth probability of person
        """
        self.ID = ID
        self.truthprob = tprob
        # trustworthy dict for each topic which is initially 0.5
        self.trustworthy = {}
        # votes dict stores the map from article ID to vote given to that article by this person
        self.votes = {}
        # register for fact checker or not
        self.isfactchecker = False

    def Register(self):
        """To register for fact checking
        """
        if not self.isfactchecker:
            self.isfactchecker = True

    def topic_trustworthy(self, topic: int):
        """Initilizing the trust worthy for new topic or return trust worthy of existing topic

        Args:
            topic (int): Topic ID

        Returns:
            float: Trust worthy of a person in this topic
        """
        if topic in self.trustworthy.keys():
            # Already existing topic
            return self.trustworthy[topic]
        else:
            # New topic
            self.trustworthy[topic] = 0.5
            return 0.5

    def vote(self, article: Article):
        """casting vote for an article

        Args:
            article (Article): Article for which he is going to cast vote

        Returns:
            bool: weather article is true or false 
        """
        if article.ID in self.votes.keys():
            # If he already voted for this article then return same vote
            return self.votes[article.ID]
        else:
            # new article to vote
            # with truthprob he will say correct
            vote = random.random() < self.truthprob
            if vote:
                # saying truth
                self.votes[article.ID] = article.truth
            else:
                # saying false
                self.votes[article.ID] = not article.truth
            return self.votes[article.ID]
    

class APP:
    """class for DApp info
    """
    def __init__(self,N: int,p: float,q: float):
        """Initilizing the App data and persons

        Args:
            N (int): Number of persons
            p (float): fraction of honest persons who are more trustworthy
            q (float): fraction of malicious people
        """
        # list for persons
        self.persons = []
        # list for articles
        self.articles = []
        num_very_trustworthy = int(p * (1-q) * N)
        num_malicious = int(q * N)
        num_normal = N - num_very_trustworthy - num_malicious
        # weights for each article
        self.weight = []
        # Adding more trustworthy people
        for i in range(num_very_trustworthy):
            person = Person(i, 0.9)
            self.persons.append(person)
        # Adding honest but less trustworthy
        for i in range(num_very_trustworthy, num_very_trustworthy + num_normal):
            person = Person(i, 0.7)
            self.persons.append(person)
        # Adding malicious person
        for i in range(num_very_trustworthy + num_normal, N):
            person = Person(i, 0.0)
            self.persons.append(person)
        # random.shuffle(self.persons)

    def Add_Article(self,news : str,topic : int, truth = True):
        """Adding new article

        Args:
            news (str): Article news
            topic (int): topic number
            truth (bool, optional): truth of article. Defaults to True.
        """
        Art = Article(len(self.articles),news,topic,truth)
        self.articles.append(Art)
    
    def committee_vote(self, article: Article, committee):
        """taking committe votes and giving the results

        Args:
            article (Article): news article
            committee (_type_): list of persons

        Returns:
            bool: result of votes from committe
        """
        votes = [person.vote(article) for person in committee]
        # taking weighted truth avg of all persons
        weighted_votes = sum([person.topic_trustworthy(article.topic) * vote for person, vote in zip(committee, votes)]) / sum([person.topic_trustworthy(article.topic) for person in committee])
        self.weight.append(weighted_votes)
        return weighted_votes > 0.5
    
    def update_trustworthiness(self, article: Article, committee,result : bool):
        """Update based trust worthiness based on result of article

        Args:
            article (Article): article
            committee (list): list of persons
            result (bool): result based on voting
        """
        committee_vote = result
        for person in committee:
            # if persons vote and overall is same then increase the trust worthiness
            if person.vote(article) == committee_vote:
                person.trustworthy[article.topic] += 0.01
                if person.trustworthy[article.topic] > 1.0:
                    person.trustworthy[article.topic] = 1.0
            # if persons vote and overall is not same then decrease the trust worthiness
            else:
                person.trustworthy[article.topic] -= 0.01
                if person.trustworthy[article.topic] < 0.0:
                    person.trustworthy[article.topic] = 0.0 

    def select_committee(self, topic : int,committee_size : int):
        """Selecting the committee

        Args:
            topic (int): Topic ID
            committee_size (int): committee size

        Returns:
            list: list of persons
        """
        active_persons = [person for person in self.persons if person.isfactchecker]
        # total reputation score
        total_reputation = sum(person.topic_trustworthy(topic) for person in active_persons)
        # each persons probabilites
        probabilities = [person.topic_trustworthy(topic) / total_reputation for person in active_persons]
        # selecting committee based on above prob
        committee = random.choices(active_persons, weights=probabilities, k=committee_size)
        # return the list
        return committee


    def RequestFactCheck(self,ID : int):
        """Request for fact checking

        Args:
            ID (int): ID of article

        Returns:
            bool: result after voting
        """
        topic = self.articles[ID].topic
        # select the committee size
        committee_size = len([person for person in self.persons if person.isfactchecker])//2
        # select committee
        committee = self.select_committee(topic, committee_size)
        # get result based on voting
        val =  self.committee_vote(self.articles[ID], committee)
        # updating the reputation
        self.update_trustworthiness(self.articles[ID], committee,val)
        # change the validity of article
        self.articles[ID].validity(val)
        return val
        

if __name__ == "__main__":
    # Adding arguments
    parser = argparse.ArgumentParser(description='DAPP Fact Checker')
    parser.add_argument('n', type=int, help='Number of Voters')
    parser.add_argument('p', type=float, help='Fraction of very trustworthy Voters') 
    parser.add_argument('q', type=float, help='Fraction of Malicious voters')
    parser.add_argument('N', type=int, help='Number of news articles to be checked before ending')
    args = parser.parse_args()
    arg1 = args.n
    arg2 = args.p
    arg3 = args.q
    N = args.N
    app = APP(arg1,arg2,arg3)
    # Adding articles
    for i in range(N):
        app.Add_Article(f'Article_{i}',0)
    # Register for fact checking
    for person in app.persons:
        person.Register()
    # request and checking the facts
    for i in range(N):
        app.RequestFactCheck(i)
    # print final trustworthy of a person
    trustval = []
    for person in app.persons:
        trustval.append(person.trustworthy[0])
        # print(person.trustworthy[0])
    # Plot for trust worthy Vs Persons 
    plt.figure()
    plt.plot([i for i in range(arg1)],trustval, marker='o', linestyle='-')
    # Adding labels and title
    plt.ylabel('Trustworthy')
    plt.xlabel('Person ID')
    plt.title('Plot trust worthy Vs Persons')
    # Displaying the graph
    # plt.grid(True)
    # plt.show()
    plt.savefig("plot.png")

    # plot for weight Vs Article ID
    plt.figure()
    plt.plot([i for i in range(N)],app.weight, marker='o', linestyle='-')
    # Adding labels and title
    plt.ylabel('Weights for articles')
    plt.xlabel('Article ID')
    plt.title('Plot weight Vs Article ID')
    # Displaying the graph
    # plt.grid(True)
    # plt.show()
    plt.savefig("Article.png")
