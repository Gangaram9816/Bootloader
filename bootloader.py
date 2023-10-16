import flet
from flet import *
import time
import serial
import os

def main(page:Page):

    ser1=serial.Serial()
    ser1.baudrate=9600
    ser1.port='COM4'
    ser1.timeout=6
    ser1.open()

    def bms_update(e):
        
        try:
            file_size = os.path.getsize('EMO_BMS_V03.bin')
            file = open('EMO_BMS_V03.bin', 'rb')
            global end_index, start_index

            loop_n=file_size//64
            last_n=file_size%64

            start_index=0
            end_index=0

            c=0
            
            print(ser1.write(b'AT+BOOT=1\r\n'))
            page.add(Text("boot1 send"))
            page.update()
            
            time.sleep(3)
            bms=ser1.readline().decode('utf-8', 'ignore')
            
            def send_data():
                global end_index, start_index
                end_index=end_index+64
                file.seek(start_index)

                chunk_data=file.read(end_index-start_index)
                
                start_index=end_index
                
                ser1.write(b'AT+BOOT=3,64')
                ser1.write(chunk_data)
                ser1.write(b'\r\n')
                print('send_data')
                
            try:
                if 'AT+DONE' in bms:
                    print('Got Done')
                    time.sleep(0.8)
                    ser1.write(b'AT+BOOT=2\r\n')
                    
                    if 'BOOTLOA' in ser1.readline().decode('utf-8', 'ignore'):
                        while c<loop_n:
                            time.sleep(0.3)

                            if send_data():
                                 
                                page.dialog = dlg
                                dlg.open = True
                                page.update()
                            else:
                                 dlg.open=False
                                 page.update()

                            if 'AT+DONE' in ser1.readline().decode('utf-8', 'ignore'):
                                c=c+1
                            else:
                                if len(page.controls)>1:
                                    for i in range(2,len(page.controls)+1):
                                        page.controls.pop()

                                page.add(Text('NOt get AT+DONE after sending chun_data ,Failed'))
                                page.update()
                                print('NOt get AT+DONE after sending chun_data ,Failed')
                                
                                break
                        file.seek(start_index)
                        
                        end_index=end_index+last_n

                        chunk_data=file.read(end_index-start_index)

                        time.sleep(0.3)

                        valu='AT+BOOT=3,'+str(last_n)
                        valu1=valu.encode()
                        
                        ser1.write(valu1)
                        ser1.write(chunk_data)
                        ser1.write(b'\r\n')
                        print('send last data')

                        time.sleep(0.3)
                        
                        if ser1.write(b'AT+BOOT=4\r\n'):
                            page.add(Text('Data send Successfully'))
                            page.update()
                        
                    else:
                        if len(page.controls)>1:
                            for i in range(2,len(page.controls)+1):
                                page.controls.pop()
                        page.add(Text('not get response after sending AT+BOOT=2'))
                        page.update()
                        print('not get response after sending AT+BOOT=2')
                        
            
                else:
                    if len(page.controls)>1:
                        for i in range(2,len(page.controls)+1):
                            page.controls.pop()
                    page.add(Text('NOt get AT+DONE after sending AT+BOOT=1 ,Failed'))
                    page.update()
                    print('NOt get AT+DONE after sending AT+BOOT=1 ,Failed')
                    
            except:
                pass

            
        except:
            pass

    dlg = AlertDialog(
        title=Text("Sending .bin files"),
    )
    
    page.add(ElevatedButton('Update BMS',on_click=bms_update))
    page.scroll='ADAPTIVE'
    page.update()
    


flet.app(target=main)
