from src import create_app
# from src.routes import routes
import os
app = create_app()

# Run the app from this file!
if __name__ == '__main__':
    # app.register_blueprint(routes, url_prefix='/')
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('APP_PORT', 500)))
    