from neo4j import GraphDatabase

class Neo4Driver:

    def __init__(self, uri, user, password):
        '''A simplified interface to a Neo4j database'''
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def __del__(self):
        self.close()

    def close(self):
        self.driver.close()

    def execute(self, cmd:str):
        '''Execute a cypher write command (std job)'''
        return self.execute_w(self._job, cmd)
    
    def execute_w(self, tFunc, cmd:str):
        '''Execute a cypher write command '''
        with self.driver.session() as session:
            return session.execute_write(tFunc, cmd)

    def execute_r(self, tFunc, cmd:str):
        '''Execute a cypher read command'''
        with self.driver.session() as session:
            return session.execute_read(tFunc, cmd)

    @staticmethod
    def _job(tx, cmd):
        return tx.run(cmd)

def getRecIds(driver:Neo4Driver)->set[int]:
    '''Returns a list of record IDs from a neo4j database'''
    label = 'lbl'
    def exec(tx, cmd):
        result = tx.run(cmd)
        vals = {r.get(label) for r in result}
        result.consume() 
        return vals
    return driver.execute_r(exec, f"MATCH (n:E31_Document) where n.P90_has_value is not null RETURN n.P90_has_value as {label}")


def countRecIds(driver:Neo4Driver)->int:
    def exec(tx, cmd):
        result = tx.run(cmd)
        return result.single().value()
    return driver.execute_r(exec, "MATCH (n:E31_Document) where n.P90_has_value is not null RETURN count(n)")

def clearNeoDB(driver:Neo4Driver)->None:
    '''Deletes all nodes in a neo4j database'''
    driver.execute("MATCH (n) DETACH DELETE n")

class Printer:

    def __init__(self):
        pass

    def execute(self, cmd:str):
        print( f"{cmd};")
        return f"{cmd};"
    
    def execute_w(self, tFunc, cmd:str):
       return self.execute(cmd)
    
    def execute_r(self, tFunc, cmd:str):
        return  self.execute(cmd)


