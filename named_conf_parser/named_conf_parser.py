# encoding=utf-8

# NamedConfig对named配置文件named.conf做了解析，将配置文件中的各个功能部分进行了分解，以便在程序中使用。
# 功能：
#     1、分解named.conf文件为几个部分：
#         pro_include_list:   option选项之前的include语句
#         options:    options选项
#         acl_list:   定义的acl列表
#         logging:    定义log输出
#         view_list:  定义view,对view内的内容进行了分解
#         end_include:    写在文件最后的include语句；注意该部分内容会最后写入文件
#     2、将修改后的NamedConfig对象转化为named.conf文件
#     3、只针对view中的include和forwarders进行了特殊处理
#

import hashlib


def md5(context):
    md5_obj = hashlib.md5()
    md5_obj.update(context)
    hash_code = md5_obj.hexdigest()
    return str(hash_code).lower()


def clear_config(config_lines):
    clear_context = []
    for one in config_lines.split('\n'):
        new_line = one
        if "//" in one:
            new_line = one.split('//')[0]
        if "#" in one:
            new_line = one.split('#')[0]
        if len(new_line) > 0:
            clear_context.append(new_line.strip())
    return ''.join(clear_context).replace('\t', ' ')


def read_named_conf(path):
    with open(path, 'r') as f:
        named_conf = f.read()
        f.close()
    return named_conf


class NamedConfig:

    def __init__(self, named_config_path):
        self.named_conf_path = named_config_path
        self.pro_include_list = []
        self.acl_list = []
        self.options = {}
        self.logging = {}
        self.view_list = []
        self.end_include_list = []
        self.raw = read_named_conf(self.named_conf_path)
        self.hash = md5(self.raw)
        self.clearConfig = clear_config(self.raw)
        self._init_config()

    def check_hash(self):
        context = read_named_conf(self.named_conf_path)
        now_hash = md5(context)
        if now_hash == self.hash:
            return True
        else:
            return False

    def _init_config(self):
        which_line = self._find_word()
        all_lines = self._sort_dirt(which_line)
        for key, info in all_lines:
            tmp = key.split()
            if tmp[0] == "include":
                if info['rp'] < which_line['options']['rp']:
                    self.pro_include_list.append((tmp[1].strip().strip('"'), info['rp']))
                else:
                    self.end_include_list.append((tmp[1].strip().strip('"'), info['rp']))
            elif tmp[0] == "acl":
                rp = info['rp']
                info.pop('rp')
                acl = {'name': tmp[1].strip(), 'rp': rp, 'list': info.keys()}
                self.acl_list.append(acl)
            elif tmp[0] == "options":
                info.pop('rp')
                self.options = info
            elif tmp[0] == "logging":
                self.logging = info
            elif tmp[0] == "view":
                view = {'name': tmp[1].strip(), 'rp': info['rp'], 'info': self._parser_view(info)}
                self.view_list.append(view)

    @staticmethod
    def _parser_view(content):
        content_d = {}
        for key, info in content.iteritems():
            # if key == "match-clients":
            #     info.pop('rp')
            #     content_d['match-clients'] = info.keys()
            # elif key == "match-destinations":
            #     info.pop('rp')
            #     content_d['match-destinations'] = info.keys()
            # elif 'recursion' in key:
            #     content_d['recursion'] = key.split()[-1]
            # elif 'forward ' in key:
            #     content_d['forward'] = key.split()[-1]
            if 'include' in key:
                if content_d.has_key('include'):
                    content_d['include'].append((key.split()[-1].strip('"'), info['rp']))
                else:
                    content_d['include'] = [(key.split()[-1].strip('"'), info['rp'])]
            elif 'forwarders' in key:
                info.pop('rp')
                content_d['forwarders'] = info.keys()
            else:
                content_d[key] = info
        return content_d

    @staticmethod
    def _sort_dirt(tmp):
        return sorted(tmp.iteritems(), key=lambda a: a[1]['rp'], reverse=False)

    def _find_word(self):
        info = {}
        rp = 0
        key_list = []
        line = ""
        for word in self.clearConfig:
            if word == ";":
                line = line.strip()
                if line == "":
                    pass
                elif not key_list:
                    info[line] = {"rp": rp}
                else:
                    current_dirt = info
                    for one_t in key_list:
                        current_dirt = current_dirt[one_t]
                    current_dirt[line] = {"rp": rp}
                line = ""
                rp += 1
            elif word == "{":
                line = line.strip()
                if not key_list:
                    info[line] = {"rp": rp}
                else:
                    current_dirt = info
                    for one_t in key_list:
                        current_dirt = current_dirt[one_t]
                    current_dirt[line] = {'rp': rp}
                key_list.append(line)
                line = ""
                rp += 1
            elif word == "}":
                key_list.pop()
                line = ""
            else:
                line += word
        return info

    @staticmethod
    def dict_to_string(self, data, tag="\t"):
        includes = []
        if 'include' in data:
            includes = sorted(data['include'], key=lambda a: a[1], reverse=False)
        forwarders = []
        if 'forwarders' in data:
            forwarders = data['forwarders']
        line = "{\n"
        tmp_data = []
        for key, info in data.iteritems():
            if key in ['rp', 'include', 'forwarders']:  # 这三个类型的数据，已经进行了特殊处理，故在此处排除掉
                continue
            tmp_data.append((key, info))
        tmp = sorted(tmp_data, key=lambda a: a[1]['rp'], reverse=False)
        for key, info in tmp:
            if len(info) > 1:
                line += (tag + key)
                line += self.dict_to_string(self, info, tag=tag + '\t')
            else:
                line += (tag + key + ';\n')
        for one in includes:
            line += (tag + 'include "%s";\n' % one[0])
        if len(forwarders) > 0:
            line += (tag + 'forwarders {%s;};\n' % (';'.join(forwarders)))
        line += (tag + '};\n')
        return line

    def tostring(self):
        named_conf_context = ""
        for one in sorted(self.pro_include_list, key=lambda b: b[1], reverse=False):
            line = 'include "%s";\n' % one[0]
            named_conf_context += line
        for one in sorted(self.acl_list, key=lambda b: b['rp'], reverse=False):
            line = "acl %s { " % one['name']
            for one1 in one['list']:
                line += '%s; ' % one1
            line += ' };\n'
            named_conf_context += line
        named_conf_context += "options "
        named_conf_context += self.dict_to_string(self, self.options)
        named_conf_context += "logging "
        named_conf_context += self.dict_to_string(self, self.logging)
        for one in sorted(self.view_list, key=lambda a: a['rp'], reverse=False):
            named_conf_context += ("view %s " % one['name'])
            named_conf_context += self.dict_to_string(self, one['info'])
        for one in sorted(self.end_include_list, key=lambda b: b[1], reverse=False):
            line = 'include "%s";\n' % one[0]
            named_conf_context += line
        return named_conf_context

    def _write_conf_file(self):
        # 将改好的配置文件写入
        with open(self.named_conf_path, 'w') as f:
            f.write(self.raw)
            f.close()

    def save(self):
        self.raw = self.tostring()
        if self.check_hash():
            self.hash = md5(self.raw)
            self._write_conf_file()
            return True
        else:
            return False


if __name__ == "__main__":
    conf = NamedConfig('../named.conf')
    print conf.logging
    print conf.tostring()
