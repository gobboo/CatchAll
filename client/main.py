import sys
import catchall

if __name__ == "__main__":
  catchall.register_blueprints()
  
  #catchall.manager.run()
  catchall.app.run()
