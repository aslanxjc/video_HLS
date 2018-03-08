#-*-coding:utf-8 -*-
import os
import time,datetime
import m3u8
import random
from ffmpy import FFmpeg
from upload_to_oss import MyOSS
import sys

reload(sys)
sys.setdefaultencoding( "utf-8" )

class TedFFmpeg(object):
    """
    """
    def __init__(self,mp4path="test.mp4"):
        """
        """
        self.oss = MyOSS()
        self.base_path= os.path.dirname(os.path.abspath(__file__))
        self.now = str(int(time.time()*1000))
        self.now_date = datetime.datetime.now() 
        self.inputs = mp4path
        self.ff = FFmpeg(
             inputs={self.inputs:"-threads 2",},
             outputs={u'{}%03d.ts'.format(self.now):'-codec copy -vbsf\
                     h264_mp4toannexb -map 0 -f segment -segment_list {}.m3u8\
                     -segment_time 10 {}%03d.ts'.format(self.now,self.now)}
        )

    def run(self):
        """
        """
        #self.ff.run()
        #转码过程
        ext = os.path.splitext(self.inputs)[-1]
        outfile = os.path.splitext(self.inputs)[0]+".mp4"
        if ext in [".flv",".avi"]:
            trans_cmd_str = "cpulimit -l 40 `ffmpeg -i {} -f avi -vcodec mpeg4 {}`".format(self.inputs,outfile)
            os.system(trans_cmd_str)

        cmd_str ="cpulimit -l 40 `ffmpeg -i {} -threads 2  -codec copy -vbsf h264_mp4toannexb \
                    -map 0 -f segment  -segment_list {}.m3u8 -segment_time 10 {}%03d.ts`"\
                    .format(self.inputs,self.now,self.now)

        #cmd_str ="ffmpeg -i {} -threads 2  -codec copy -vbsf h264_mp4toannexb -map 0 -f segment  -segment_list {}.m3u8 -segment_time 10 {}%03d.ts".format(self.inputs,self.now,self.now)

        print cmd_str,88888888888888888888888

        os.system(cmd_str)

        self.m3u8_file_name = os.path.join(os.path.dirname(self.base_path),"{}.m3u8".format(self.now))
        #截取第一个图片
        os.system(u"ffmpeg -i {} -y -f  image2  -ss 00:00:01 -vframes 1  {}.png".format(self.inputs,self.now))
        self.first_image_name = os.path.join(os.path.dirname(self.base_path),"{}.png".format(self.now))
        return self.m3u8_file_name

    def get_ts_files(self):
        """
        """
        _tss = []
        m3u8_obj = m3u8.load(self.m3u8_file_name)
        for _s in m3u8_obj.segments:
            _spath = os.path.join(os.path.dirname(self.base_path),_s.uri)
            _tss.append(_spath)
        return _tss

    def generate_captcha(self,code_type, length=6):                                                     
        """                                                                                        
        随机生成6位验证码                                                                          
        """                                                                                        
        code_list = []                                                                             
                                                                                                   
        if code_type == "mix":                                                                     
            _length = length / 3                                                                   
            for i in range(_length):                                                               
                code_list.append(str(random.randint(0, 9)))                                        
                code_list.append(chr(random.randint(65, 90)))                                      
                code_list.append(chr(random.randint(97, 122)))                                     
        else:                                                                                      
            for i in range(length):                                                                
                code_list.append(str(random.randint(0, 9)))                                        
                                                                                                   
        return "".join(code_list)


    def gen_date_path(self):
        """
        """
        now_path = "{}/{}/{}/{}".format(self.now_date.year,self.now_date.month
                    ,self.now_date.day,self.generate_captcha("mix",9))
        return now_path


    def upload_to_cloud(self):
        """将本地的m3u8及ts文件上传到云端
        """
        self._gen_date_path = self.gen_date_path()
        #上传m3u8文件
        m3u8_ossfile = os.path.join(
                    self._gen_date_path,
                    os.path.split(self.m3u8_file_name)[-1]
                    )
        m3u8_url = self.oss.upload_from_local(self.m3u8_file_name,m3u8_ossfile)
        print m3u8_url
        #上传截取的第一张图片
        first_image_ossfile = os.path.join(
                    self._gen_date_path,
                    os.path.split(self.first_image_name)[-1]
                    )
        first_image_name = self.oss.upload_from_local(self.first_image_name,first_image_ossfile)
        print first_image_name,8888888888888888
        #上传ts文件
        _tss = self.get_ts_files()
        for _ts in _tss:
            _ts_ossfile = os.path.join(self._gen_date_path,os.path.split(_ts)[-1])
            self.oss.upload_from_local(_ts,_ts_ossfile)
            os.remove(_ts)

        #os.remove(self.m3u8_file_name)
        #os.remove(self.first_image_name)

        return m3u8_url

if __name__ == "__main__":
    tedff = TedFFmpeg()
    tedff.run()
    tedff.upload_to_cloud()
    
