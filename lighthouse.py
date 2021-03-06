# 
#  lighthouse.py
#  Python Lighthouse API
#
#  Lighthouse simple hosted issue tracking, bug tracking, and project
#   management software.
#
#  They also have an XML-based API for working with your projects
#  
#  http://lighthouseapp.com
#  http://lighthouseapp.com/api
#
#  Created by Clinton Ecker on 2009-01-31.
#  Copyright 2009 Clint Ecker. All rights reserved.
# 
# //////////////////////////////////////////////////////////////////////
# 
#  Modified Version by Kjuly ( Kj Yu )
#  Author URL : http://kjuly.com
#
#  Description: 
#    It's modified and used for DevStats Project( thePlant Co. Ltd. )
#
#  Added Funs:
#    User
# 
import urllib2
from urllib2 import HTTPError
import os.path
import pprint
from xmltodict import xmltodict
#from dateutil.parser import *
#from dateutil.tz import *


class Lighthouse(object):
    """The main lighthouse object for managing the connection"""
    
    def __init__(self, token=None, url=None):
        #super(Lighthouse, self).__init__()
        self.token      = token
        self.url        = url
        self.projects   = []
        self.user       = User()
        self.token_tail = None #'_token=%s' % self.token
    
    def _datetime(self, data):
        """Returns a datetime object representation of string
        
        >>> lh = Lighthouse()
        >>> lh._datetime('2008-09-25T20:04:13+01:00')
        datetime.datetime(2008, 9, 25, 20, 4, 13, tzinfo=tzoffset(None, 3600))
        >>> lh._datetime('2009-01-26T16:47:00-08:00')
        datetime.datetime(2009, 1, 26, 16, 47, tzinfo=tzoffset(None, -28800))
        >>> lh._datetime('2009-01-31T15:42:18-08:00')
        datetime.datetime(2009, 1, 31, 15, 42, 18, tzinfo=tzoffset(None, -28800))
        """
        #return parse(data)
        pass
    
    def _integer(self, data):
        """Returns a literal integer object from a string"
        
        >>> lh = Lighthouse()
        >>> lh._integer('10')
        10
        >>> lh._integer('True')
        Traceback (most recent call last):
        ...
        ValueError: invalid literal for int() with base 10: 'True'
        >>> lh._integer('23.5')
        Traceback (most recent call last):
        ...
        ValueError: invalid literal for int() with base 10: '23.5'
        """""
        if data:
            return int(data,10)
        else:
            return None
    
    def _boolean(self, data):
        """Returns True or False from a string
        
        >>> lh = Lighthouse()
        >>> lh._boolean('1')
        True
        >>> lh._boolean('2')
        False
        >>> lh._boolean('true')
        True
        >>> lh._boolean('True')
        True
        >>> lh._boolean('false')
        False
        >>> lh._boolean('False')
        False
        >>> lh._boolean(1)
        True
        >>> lh._boolean(2)
        False
        >>> lh._boolean(0)
        False
        """
        if data == 'true' or data == 'True' or data == '1' or data == 1:
            return True
        else:
            return False
    
    def _string(self, data):
        """Returns a...uh string from a bit of data
        
        >>> lh = Lighthouse()
        >>> lh._string('lol')
        'lol'
        >>> lh._string(1)
        '1'
        >>> lh._string(True)
        'True'
        >>> lh._string('2008-09-25T20:04:13+01:00')
        '2008-09-25T20:04:13+01:00'
        >>> lh._datetime('2008-09-25T20:04:13+01:00')
        datetime.datetime(2008, 9, 25, 20, 4, 13, tzinfo=tzoffset(None, 3600))
        >>> lh._string(_)
        '2008-09-25 20:04:13+01:00'
        """
        return str(data)

    def _yaml(self, data):
        return self._string(data)
    
    def _nil(self, data):
        """Returns None
        
        >>> lh = Lighthouse()
        >>> lh._nil('lol')
        >>> lh._nil(1)
        >>> lh._nil(True)
        >>> lh._nil('2008-09-25T20:04:13+01:00')
        >>> lh._datetime('2008-09-25T20:04:13+01:00')
        datetime.datetime(2008, 9, 25, 20, 4, 13, tzinfo=tzoffset(None, 3600))
        >>> lh._nil(_)
        """
        return None
    
    def _array(self, data):
        """Returns an array
        """
        r = []
        for item in data['children']:
            item_obj = {}
            for field in item['children']:
                field_name, field_value, field_type = self._parse_field(field)
                item_obj[field_name.replace('-', '_')] = field_value
            r.append(item_obj)
        return r

    def _get_data(self, path):
        """Takes a path, joins it with the project's URL and grabs that 
        resource's XML data
        
        >>> lh = Lighthouse()
        >>> lh._get_data('projects.xml')
        Traceback (most recent call last):
        ...
        ValueError: Please set url properly
        >>> lh.url = 'http://ars.lighthouseapp.com'
        >>> lh._get_data('projectx.xml')
        Traceback (most recent call last):
        ...
        ExpatError: mismatched tag: line 30, column 4
        >>> lh.url = 'http://example.com'
        >>> lh._get_data('projects.xml')
        Traceback (most recent call last):
        ...
        HTTPError: HTTP Error 404: Not Found
        """
        if self.url != None:
            endpoint = os.path.join(self.url, path)
            #req = urllib2.Request(endpoint)
            if self.token:
                if endpoint[-3:] == 'xml' :
                    endpoint = '%s?%s' % ( endpoint, self.token_tail )
                else :
                    endpoint = '%s&%s' % ( endpoint, self.token_tail )
                #req.add_header('X-LighthouseToken', self.token)
            req  = urllib2.Request(endpoint)
            resp = urllib2.urlopen(req)
            data = resp.read()
            return self._parse_xml(data)
        else:
            raise ValueError('Please set url properly')
    
    def _post_data(self, path, data):
        if self.url == None:
            raise ValueError('Please set url properly')
        if self.token == None:
            raise ValueError('Please set token properly')
        endpoint = os.path.join(self.url, path)
        headers = { 
            'Content-Type' : 'application/xml',
            'X-LighthouseToken' : self.token,
        }
        req = urllib2.Request(endpoint, data, headers)
        try:
            response = urllib2.urlopen(req)
        except HTTPError, response:
            if response.code == 201:
                data = response.read()
            else:
                raise
        else:
            raise
        return self._parse_xml(data)
            
    def _parse_xml(self, xmldata):
        return xmltodict(xmldata)
    
    def _parse_field(self, field):
        field_type = None
        field_name = None
        field_attributes = None
        converter = None
        
        attributes = field.get('attributes', {})
        field_value = field.get('cdata', None)
        field_name = field.get('name', None)
        
        if attributes:
            field_type = attributes.get('type', None)

        if field_type == "array":
            field_value = self._array(field)

        elif field_type and (field_value is not None):
            if field_type == "datetime" :
                field_value = str(field_value)
            else :
                converter = getattr(self,'_'+field_type)
                field_value = converter(field_value)
        """
        print( field_name )
        print( field_type )
        print( field_value )
        print( '-------------' )
        """
        
        return (field_name, field_value, field_type)
    
    def init(self):
        """Pulls in all the projects available and populates them with
        their properties"""
        self.get_projects()
        return
        
    def fetch_members(self) :
        for p in self.projects :
            self.get_members( p ) # Get Members
        return

    def fetch_tickets(self) :
        """Pulls in all the tickets available and populates them with
        their properties"""
        for p in self.projects :
            self.get_tickets( p )
        return

    def fetch_all_tickets(self, page_start, page_end) :
        """Pulls in all the tickets available and populates them with
        their properties"""
        for p in self.projects :
            self.get_all_tickets( p, page_start, page_end )
        return

    def get_projects(self):
        """Retrieves all available projects
        
        >>> lh = Lighthouse()
        >>> lh.url = 'http://ars.lighthouseapp.com'
        >>> lh.init()
        >>> project = lh.projects[0]
        >>> len(lh.projects)
        1
        >>> project.name
        'Ars Technica 5.0'
        """
        path = Project.endpoint
        project_list = self._get_data(path)
        projects = []
        if project_list.has_key('children') :
            for project in project_list['children']:
                p_obj = Project()
                for field in project['children']:
                    field_name, field_value, field_type = self._parse_field(field)
                    p_obj.__setattr__(field_name.replace('-', '_'), field_value)
                projects.append(p_obj)
            self.projects = projects
        return
    
    def get_all_tickets(self, project, page_start, page_end):
        """Populates the project with all existing tickets
        
        >>> lh = Lighthouse()
        >>> lh = Lighthouse()
        >>> lh.url = 'http://ars.lighthouseapp.com'
        >>> lh.init()
        >>> project = lh.projects[0]
        >>> lh.get_all_tickets(project)
        
        >>>
        """
        c = 30
        page = page_start
        ticket_count = 0
        while c == 30 and page < page_end :
            c = self.get_tickets(project, page)
            ticket_count += c
            page += 1
        
    def get_tickets(self, project, page=1):
        """Retrieves all the tickets in a project
        
        >>> lh = Lighthouse()
        >>> lh.url = 'http://ars.lighthouseapp.com'
        >>> lh.init()
        >>> project = lh.projects[0]
        >>> lh.get_tickets(project)
        30
        >>> lh.get_tickets(project, 2)
        30
        >>> lh.get_tickets(project, 1000)
        0
        >>> lh.get_tickets(project, 0)
        Traceback (most recent call last):
        ...
        ValueError: Page number should be 1-indexed
        >>> lh.get_tickets(project, -1)
        Traceback (most recent call last):
        ...
        ValueError: Page number should be 1-indexed
        >>> lh.get_tickets(project, '1')
        Traceback (most recent call last):
        ...
        TypeError: Page number should be of type Integer
        >>> lh.get_tickets(123)
        Traceback (most recent call last):
        ...
        TypeError: Project must be instance of Project object
        >>> lh.get_tickets('project')
        Traceback (most recent call last):
        ...
        TypeError: Project must be instance of Project object
        """
        if not isinstance(project, Project):
            raise TypeError('Project must be instance of Project object')
        if not isinstance(page, int):
            raise TypeError('Page number should be of type Integer')
        if page <= 0:
            raise ValueError('Page number should be 1-indexed')
        path = Ticket.endpoint % (project.id)
        ticket_list = self._get_data(path+"?page=" + str(page))
        c = 0
        if(ticket_list.get('children', None)):
            for ticket in ticket_list['children']:
                c += 1
                if( ticket.get('children', None) ): # Got the KeyError 'children', so check whether it exists
                    t_obj = Ticket()
                    for field in ticket['children']:
                        field_name, field_value, field_type = \
                            self._parse_field(field)
                        py_field_name = field_name.replace('-', '_')
                        t_obj.__setattr__(py_field_name, field_value)
                        t_obj.fields.add(py_field_name)
                    project.tickets[t_obj.number] = t_obj
        return c

    def get_full_ticket(self, project, ticket):
        path = Ticket.endpoint_single % (project.id, ticket.number)
        ticket_data = self._get_data(path)

        for field in ticket_data['children']:
            field_name, field_value, field_type = self._parse_field(field)
            py_field_name = field_name.replace('-', '_')
            ticket.__setattr__(py_field_name, field_value)
            ticket.fields.add(py_field_name)

        return ticket
            
    def get_user( self ) :
        """Retrieves the tokens
        """
        path    = User.endpoint_token % ( self.token )
        token   = self._get_data( path )

        if( token.get('children', None) ) :
            for field in token['children'] :
                #m_obj = User()
                field_name, field_value, field_type = self._parse_field( field )
                py_field_name = field_name.replace('-', '_')
                self.user.__setattr__( py_field_name, field_value )
                self.user.fields.add( py_field_name )
            #project.user.append( m_obj )
            #self.user = m_obj

    def get_members( self, project ) :
        """Retrieves all the members in a project
        """
        if not isinstance(project, Project):
            raise TypeError('Project must be instance of Project object')

        path = Member.endpoint_proj % ( project.id )
        member_list = self._get_data( path ) # Has page or not ?

        if( member_list.get('children', None) ) :
            for member in member_list['children'] :
                m_obj = Member()
                for field in member['children']:
                    field_name, field_value, field_type = self._parse_field( field )
                    # Deep into sub level
                    if( field.get('children', None) ) :
                        set_sub = {}
                        for field_sub in field['children'] :
                            field_name_s, field_value_s, field_type_s = self._parse_field( field_sub )
                            py_field_name_s = field_name_s.replace('-', '_')
                            set_sub[ py_field_name_s ] = field_value_s
                        m_obj.__setattr__( field_name, set_sub )
                        m_obj.fields.add( field_name )

                    else :
                        py_field_name = field_name.replace('-', '_')
                        m_obj.__setattr__( py_field_name, field_value )
                        m_obj.fields.add( py_field_name )
                project.members.append( m_obj )

    def get_users(self, name):
        pass
        
    def add_ticket(self, project=None, title=None, body=None):
        if project is None or isinstance(project, str):
            if(len(self.projects) == 0):
                self.init()
            project = self.projects[0]
            project_id = project.id
        elif isinstance(project, int):
            project_id = project
        elif isinstance(project, Project):
            project_id = project.id
        else:
            raise ValueError('Couldn\'t find a project matching \''+project+'\'')
        path = Ticket.endpoint % (project_id,)
        data = Ticket.creation_xml % {
            'body':body, 
            'title':title,
        }
        new_ticket = self._post_data(path, data)
        t_obj = Ticket()
        for field in new_ticket['children']:
            field_name, field_value, field_type = \
                self._parse_field(field)
            t_obj.__setattr__(field_name.replace('-', '_'),\
                field_value)
        return t_obj
    
class Ticket(object):
    """Tickets are individual issues or bugs"""
    
    endpoint = 'projects/%d/tickets.xml'
    endpoint_single = 'projects/%d/tickets/%d.xml'
    creation_xml = """<ticket>
    <body>%(body)s</body>
    <title>%(title)s</title>
</ticket>"""
    def __init__(self):
        super(Ticket, self).__init__()
        self.versions = []
        self.attachments = []
        self.fields = set()
        
    def __repr__(self):
        if self.title:
            return "Ticket: %s" % (self.title,)
        else:
            return "Ticket: Unnamed"
        
    def to_json_obj(self):
        return dict([(f, getattr(self, f)) for f in self.fields])
    
class Project(object):
    """Projects contain milestones, tickets, messages, and changesets"""
    
    endpoint = 'projects.xml'
    
    def __init__(self):
        super(Project, self).__init__()
        self.tickets = {}
        self.members = []   # Members
        self.milestones = []
        self.messages = []

    def __repr__(self):
        if self.name:
            return "Project: %s" % (self.name,)
        else:
            return "Project: Unnamed"

class Milestone(object):
    """Milestones reference tickets"""
    def __init__(self, arg):
        super(Milestone, self).__init__()
        self.arg = arg
        
class Message(object):
    """Messages are notes"""
    def __init__(self, arg):
        super(Message, self).__init__()
        self.arg = arg
        
class Member(object):
    """A Member"""
    endpoint_proj = 'projects/%d/memberships.xml'
    endpoint_user = 'users/%d/memberships.xml'

    def __init__( self ) :
        super( Member, self ).__init__()
        self.fields = set()

class User(object):
    """A user"""
    endpoint_token  = 'tokens/%s.xml'
    endpoint_user   = 'users/%d.xml'

    def __init__( self ):
        super(User, self).__init__()
        self.fields = set();
        
if __name__ == "__main__":
    import doctest
    doctest.testmod(optionflags=doctest.IGNORE_EXCEPTION_DETAIL)
