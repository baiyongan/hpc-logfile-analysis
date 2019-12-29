为了对用户信息及队列信息的进行安全处理，将JustQueue_bhist_2019_original.out 相应的用户名替换为随机名 user_dddnnn 的格式，
但是有的用户，如60056082， 60056206 其源日志文件中，部分任务的用户名是被行分隔了的，sed替换不全，懒得改了。

就这样吧，谁稀罕这俩用户信息，不分析不就好了。

lsfadmin 是管理员用户，权限很大，各种用户间切换来切换去的，不用分析

60056082 对应 user_739trw
60056206 对应 user_762frq

想分析，自己在JustQueue-bhist-2019-all.log文件中再次sed即可

sed -i  's/60056082/user_739trw/g'  JustQueue-bhist-2019-all.log
sed -i 's/60056206/user_762frq/g'   JustQueue-bhist-2019-all.log
