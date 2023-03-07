from flask import Flask, request, jsonify
from flask.views import MethodView
from sqlalchemy import Column, DateTime, Integer, create_engine, String, func
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask('app')
app.config['JSON_AS_ASCII'] = False
DSN = 'postgresql://admin:admin_pass@127.0.0.1:5430/adv_db'
engine = create_engine(DSN)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class AdModel(Base):
    
    __tablename__ = 'ads'
    id = Column(Integer, primary_key=True)
    header = Column(String(50), nullable=False)
    description = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    owner = Column(String(50), nullable=False)

    def __repr__(self):
        return f'AdModel: {self.header}'

    def to_dict(self):
        return {
            'id': self.id,
            'header': self.header,
            'description': self.description,
            'created_at': self.created_at,
            'owner': self.owner
        }


Base.metadata.create_all(engine)


class HttpError(Exception):

    def __init__(self, error_code, message):

        self.error_code = error_code
        self.message = message


@app.errorhandler(HttpError)
def handle_error(error):
    response = jsonify({'message': error.message})
    response.status_code = error.status_code
    return response


class AdView(MethodView):

    def get(self, adv_id=None):

        with Session() as session:
            if adv_id is None:
                ads = session.query(AdModel).all()
            else:
                ads = session.query(AdModel).filter(AdModel.id==adv_id)
            return jsonify([ad.to_dict() for ad in ads])


    def post(self):

        new_ad_data = request.json
        with Session() as session:
            new_ad = AdModel(**new_ad_data)
            session.add(new_ad)
            session.commit()
            return jsonify({
                'id': new_ad.id,
                'header': new_ad.header,
                    })
    
    
    def delete(self, adv_id):

        with Session() as session:
            try:
                ads = session.query(AdModel).filter_by(id=adv_id).one()
                session.delete(ads)
                session.commit()
                return f'объявление №{adv_id} удалено из базы'
            except NoResultFound:
                return f'объявление №{adv_id} отсутствует'



app.add_url_rule('/ad/', view_func=AdView.as_view('create, get'), methods=['POST', 'GET'])
app.add_url_rule('/ad/<int:adv_id>', view_func=AdView.as_view('get_ad'), methods=['GET', 'DELETE'])


app.run()
